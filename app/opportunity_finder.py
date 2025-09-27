import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.models import (User, UserSkill, Skill, JobOpportunity, 
                       UserOpportunity, LearningResource)
from app import db
import json
from datetime import datetime, timedelta
import re

class OpportunityFinder:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=500)
    
    def find_opportunities(self, user_id, limit=20):
        """Find relevant opportunities for a user"""
        user = User.query.get(user_id)
        if not user:
            return {"error": "User not found"}
        
        # Get job matches
        job_matches = self._find_job_matches(user, limit)
        
        # Save opportunities
        self._save_user_opportunities(user_id, job_matches)
        
        # Generate recommendations
        recommendations = self._generate_opportunity_recommendations(job_matches, user)
        
        # Get applied filters
        filters = self._get_applied_filters(user)
        
        return {
            'opportunities': job_matches,
            'recommendations': recommendations,
            'filters_applied': filters,
            'total_matches': len(job_matches)
        }
    
    def _find_job_matches(self, user, limit):
        """Find matching job opportunities"""
        # Get user's skills and preferences
        user_skills = self._get_user_skill_vector(user.id)
        preferences = self._get_user_preferences(user)
        
        # Get recent job opportunities
        jobs = JobOpportunity.query.filter(
            JobOpportunity.expires_date > datetime.utcnow()
        ).order_by(JobOpportunity.posted_date.desc()).limit(100).all()
        
        job_matches = []
        
        for job in jobs:
            match_result = self._calculate_job_match(job, user, user_skills, preferences)
            if match_result['match_score'] >= 0.5:  # Only include good matches
                job_matches.append({
                    'id': job.id,
                    'title': job.title,
                    'company': job.company,
                    'location': job.location,
                    'salary_range': f"${job.salary_min:,} - ${job.salary_max:,}" if job.salary_min and job.salary_max else "Not specified",
                    'description': job.description,
                    'url': job.url,
                    'posted_date': job.posted_date,
                    'remote_ok': job.remote_ok,
                    'match_score': match_result['match_score'],
                    'skill_matches': match_result['skill_matches'],
                    'missing_skills': match_result['missing_skills'],
                    'explanation': match_result['explanation']
                })
        
        return sorted(job_matches, key=lambda x: x['match_score'], reverse=True)[:limit]
    
    def _get_user_skill_vector(self, user_id):
        """Create skill vector for user"""
        skills = db.session.query(Skill.name, UserSkill.proficiency_level)\
                          .join(UserSkill)\
                          .filter(UserSkill.user_id == user_id)\
                          .all()
        
        return {name: level for name, level in skills}
    
    def _get_user_preferences(self, user):
        """Get user job preferences"""
        return {
            'target_role': user.target_role,
            'target_salary': user.target_salary,
            'location': user.location,
            'experience_years': user.experience_years
        }
    
    def _calculate_job_match(self, job, user, user_skills, preferences):
        """Calculate how well a job matches a user"""
        # Extract required skills
        required_skills = self._extract_job_skills(job)
        
        # Calculate different match components
        skill_match_data = self._calculate_skill_match(user_skills, required_skills)
        title_match = self._calculate_title_match(job.title, preferences['target_role'])
        location_match = self._calculate_location_match(job.location, preferences['location'])
        salary_match = self._calculate_salary_match(job, preferences['target_salary'])
        experience_match = self._calculate_experience_match(job, preferences['experience_years'])
        
        # Weight the components
        weights = {
            'skills': 0.4,
            'title': 0.2,
            'location': 0.15,
            'salary': 0.15,
            'experience': 0.1
        }
        
        match_components = {
            'skills': skill_match_data['match_score'],
            'title': title_match,
            'location': location_match,
            'salary': salary_match,
            'experience': experience_match
        }
        
        # Calculate final score
        match_score = sum(score * weights[component] 
                         for component, score in match_components.items())
        
        return {
            'match_score': round(match_score, 2),
            'skill_matches': skill_match_data['matching_skills'],
            'missing_skills': skill_match_data['missing_skills'],
            'explanation': self._generate_match_explanation(match_components, skill_match_data)
        }
    
    def _extract_job_skills(self, job):
        """Extract required skills from job posting"""
        if job.requirements:
            return json.loads(job.requirements)
        
        # Basic skill extraction if no structured requirements
        common_skills = [
            'python', 'java', 'javascript', 'sql', 'html', 'css', 'react', 'node.js',
            'aws', 'azure', 'docker', 'kubernetes', 'agile', 'scrum', 'git'
        ]
        
        found_skills = []
        if job.description:
            description_lower = job.description.lower()
            for skill in common_skills:
                if skill in description_lower:
                    found_skills.append(skill)
        
        return found_skills
    
    def _calculate_skill_match(self, user_skills, job_requirements):
        """Calculate skill match between user and job"""
        if not job_requirements:
            return {
                'match_score': 0.5,  # Neutral score if no requirements
                'matching_skills': [],
                'missing_skills': []
            }
        
        matching_skills = []
        missing_skills = []
        
        for skill in job_requirements:
            if skill.lower() in {s.lower() for s in user_skills.keys()}:
                matching_skills.append(skill)
            else:
                missing_skills.append(skill)
        
        if not job_requirements:
            match_score = 0.5
        else:
            match_score = len(matching_skills) / len(job_requirements)
        
        return {
            'match_score': match_score,
            'matching_skills': matching_skills,
            'missing_skills': missing_skills
        }
    
    def _calculate_title_match(self, job_title, target_role):
        """Calculate how well job title matches target role"""
        if not target_role or not job_title:
            return 0.5
        
        # Clean and normalize titles
        job_title = job_title.lower()
        target_role = target_role.lower()
        
        # Direct match
        if job_title == target_role:
            return 1.0
        
        # Partial match
        job_words = set(re.findall(r'\w+', job_title))
        target_words = set(re.findall(r'\w+', target_role))
        
        if not job_words or not target_words:
            return 0.5
        
        overlap = len(job_words & target_words)
        overlap_score = overlap / max(len(job_words), len(target_words))
        
        return min(0.8, overlap_score * 2)  # Cap at 0.8 for partial matches
    
    def _calculate_location_match(self, job_location, user_location):
        """Calculate location match score"""
        if not job_location or not user_location:
            return 0.5
        
        job_location = job_location.lower()
        user_location = user_location.lower()
        
        # Exact match
        if job_location == user_location:
            return 1.0
        
        # Check if same city/state
        job_parts = set(re.findall(r'\w+', job_location))
        user_parts = set(re.findall(r'\w+', user_location))
        
        if job_parts & user_parts:
            return 0.8
        
        # Check if remote
        if 'remote' in job_location.lower():
            return 0.9
        
        return 0.2  # Different locations
    
    def _calculate_salary_match(self, job, target_salary):
        """Calculate salary match score"""
        if not target_salary or not job.salary_min:
            return 0.5
        
        if job.salary_min <= target_salary <= job.salary_max:
            return 1.0
        
        if job.salary_max < target_salary:
            ratio = job.salary_max / target_salary
            return max(0.2, ratio)  # At least 0.2 if there's any salary
        
        # Job pays more than target
        return 0.9
    
    def _calculate_experience_match(self, job, user_experience_years):
        """Calculate experience level match"""
        if not user_experience_years:
            return 0.5
            
        # Extract experience requirement from job description
        if not job.description:
            return 0.5
            
        description_lower = job.description.lower()
        
        # Look for experience requirements in the description
        exp_patterns = [
            r'(\d+)\+?\s*years?(?:\s+of)?\s+experience',
            r'(\d+)\+?\s*years?(?:\s+of)?\s+work\s+experience',
            r'experience:\s*(\d+)\+?\s*years?'
        ]
        
        required_years = None
        for pattern in exp_patterns:
            match = re.search(pattern, description_lower)
            if match:
                required_years = int(match.group(1))
                break
        
        if not required_years:
            return 0.5
        
        if user_experience_years >= required_years:
            return 1.0
        
        ratio = user_experience_years / required_years
        return max(0.3, ratio)  # At least 0.3 if they have some experience
    
    def _generate_match_explanation(self, match_components, skill_match_data):
        """Generate human-readable explanation of match score"""
        explanations = []
        
        # Skill match explanation
        if skill_match_data['matching_skills']:
            explanations.append(
                f"You have {len(skill_match_data['matching_skills'])} of the required skills: "
                f"{', '.join(skill_match_data['matching_skills'][:3])}..."
            )
        if skill_match_data['missing_skills']:
            explanations.append(
                f"Consider learning: {', '.join(skill_match_data['missing_skills'][:3])}"
            )
        
        # Other components
        if match_components['title'] > 0.8:
            explanations.append("Job title closely matches your target role")
        if match_components['location'] > 0.8:
            explanations.append("Location is ideal")
        if match_components['salary'] > 0.8:
            explanations.append("Salary matches your expectations")
        if match_components['experience'] > 0.8:
            explanations.append("Your experience level is a good match")
        
        return "; ".join(explanations)
    
    def _save_user_opportunities(self, user_id, opportunities):
        """Save opportunities for user tracking"""
        for opp in opportunities:
            # Check if already exists
            existing = UserOpportunity.query.filter_by(
                user_id=user_id,
                opportunity_id=opp['id']
            ).first()
            
            if not existing:
                user_opp = UserOpportunity(
                    user_id=user_id,
                    opportunity_id=opp['id'],
                    match_score=opp['match_score']
                )
                db.session.add(user_opp)
        
        db.session.commit()
    
    def get_user_opportunities(self, user_id, limit=20):
        """Get opportunities for a user, including saved and matched ones"""
        # Get saved opportunities
        saved_opps = UserOpportunity.query.filter_by(user_id=user_id)\
            .order_by(UserOpportunity.match_score.desc())\
            .limit(limit)\
            .all()
        
        opportunities = []
        for uo in saved_opps:
            job = JobOpportunity.query.get(uo.opportunity_id)
            if job:
                opportunities.append({
                    'id': job.id,
                    'title': job.title,
                    'company': job.company,
                    'location': job.location,
                    'salary_range': f"${job.salary_min:,} - ${job.salary_max:,}" if job.salary_min and job.salary_max else "Not specified",
                    'description': job.description,
                    'url': job.url,
                    'posted_date': job.posted_date,
                    'remote_ok': job.remote_ok,
                    'match_score': uo.match_score,
                    'status': uo.status
                })
        
        # If we don't have enough saved opportunities, find new ones
        if len(opportunities) < limit:
            new_matches = self.find_opportunities(user_id, limit - len(opportunities))
            if 'opportunities' in new_matches:
                opportunities.extend(new_matches['opportunities'])
        
        return opportunities

    def _get_applied_filters(self, user):
        """Get filters that were applied during search"""
        filters = []
        
        if user.target_role:
            filters.append(f"Role: {user.target_role}")
        if user.location:
            filters.append(f"Location: {user.location}")
        if user.target_salary:
            filters.append(f"Minimum Salary: ${user.target_salary:,}")
        if user.experience_years:
            filters.append(f"Experience: {user.experience_years}+ years")
            
        return filters
    
    def _generate_opportunity_recommendations(self, opportunities, user):
        """Generate recommendations based on opportunities found"""
        if not opportunities:
            return []
        
        recommendations = []
        
        # Analyze skill gaps
        all_required_skills = []
        for opp in opportunities[:10]:  # Look at top 10 matches
            all_required_skills.extend(opp.get('missing_skills', []))
        
        if all_required_skills:
            skill_freq = pd.Series(all_required_skills).value_counts()
            top_missing_skills = skill_freq.head(3).index.tolist()
            
            recommendations.append({
                'type': 'skill_development',
                'title': 'Recommended Skills to Develop',
                'description': f"Focus on learning these skills to increase your job matches: {', '.join(top_missing_skills)}",
                'priority': 'high'
            })
        
        # Salary insights
        salary_ranges = []
        for opp in opportunities:
            if isinstance(opp.get('salary_range'), str) and '-' in opp['salary_range']:
                try:
                    min_sal = int(opp['salary_range'].split('-')[0].strip('$ ').replace(',', ''))
                    max_sal = int(opp['salary_range'].split('-')[1].strip('$ ').replace(',', ''))
                    salary_ranges.append((min_sal + max_sal) / 2)
                except:
                    continue
        
        if salary_ranges:
            avg_salary = sum(salary_ranges) / len(salary_ranges)
            if user.target_salary and avg_salary < user.target_salary:
                recommendations.append({
                    'type': 'salary_insight',
                    'title': 'Salary Expectations',
                    'description': f"Consider adjusting your target salary (${user.target_salary:,}). The average salary for matching positions is ${avg_salary:,.0f}",
                    'priority': 'medium'
                })
        
        # Location insights
        remote_jobs = [opp for opp in opportunities if opp.get('remote_ok')]
        if remote_jobs and len(remote_jobs) / len(opportunities) > 0.3:
            recommendations.append({
                'type': 'location_insight',
                'title': 'Remote Opportunities',
                'description': f"Consider remote positions to increase your opportunities. {len(remote_jobs)} remote positions found.",
                'priority': 'medium'
            })
        
        return recommendations