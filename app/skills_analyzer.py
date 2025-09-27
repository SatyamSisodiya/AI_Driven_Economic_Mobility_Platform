import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.models import User, UserSkill, Skill, JobOpportunity, SkillGapAnalysis
from app import db
import json
from datetime import datetime

class SkillsAnalyzer:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
    
    def analyze_skill_gaps(self, user_id, target_role=None):
        """Analyze skill gaps for a user based on their target role and market demand"""
        user = User.query.get(user_id)
        if not user:
            return {"error": "User not found"}
        
        target_role = target_role or user.target_role
        if not target_role:
            return {"error": "No target role specified"}
            
        # Get current skills
        current_skills = self._get_user_skills(user_id)
        
        # Get required skills for target role
        required_skills = self._get_required_skills_for_role(target_role)
        
        # Calculate skill gaps
        skill_gaps = self._calculate_skill_gaps(current_skills, required_skills)
        
        # Get market insights
        market_insights = self._get_market_insights(target_role)
        
        # Generate recommendations
        recommendations = self._generate_skill_recommendations(skill_gaps, market_insights)
        
        # Save analysis
        analysis = SkillGapAnalysis(
            user_id=user_id,
            target_role=target_role,
            analysis_data=json.dumps({
                'skill_gaps': skill_gaps,
                'market_insights': market_insights
            }),
            recommendations=json.dumps(recommendations),
            priority_skills=json.dumps(self._get_priority_skills(skill_gaps))
        )
        db.session.add(analysis)
        db.session.commit()
        
        return {
            'skill_gaps': skill_gaps,
            'market_insights': market_insights,
            'recommendations': recommendations,
            'priority_skills': self._get_priority_skills(skill_gaps)
        }
    
    def _get_user_skills(self, user_id):
        """Get current skills for a user"""
        skills = db.session.query(Skill.name, UserSkill.proficiency_level)\
                          .join(UserSkill)\
                          .filter(UserSkill.user_id == user_id)\
                          .all()
        
        skills_dict = {}
        for name, level in skills:
            skills_dict[name] = {
                'proficiency': level,
                'status': 'current'
            }
            
        return skills_dict
    
    def _get_required_skills_for_role(self, target_role):
        """Get comprehensive market insights and required skills for a target role"""
        jobs = JobOpportunity.query.filter(
            JobOpportunity.title.ilike(f"%{target_role}%")
        ).limit(100).all()
        
        skill_data = {}
        total_jobs = len(jobs)
        
        for job in jobs:
            requirements = json.loads(job.requirements) if job.requirements else []
            salary_avg = (job.salary_min + job.salary_max) / 2 if job.salary_min and job.salary_max else None
            
            for skill in requirements:
                if skill not in skill_data:
                    skill_data[skill] = {
                        'frequency': 0,
                        'salaries': [],
                        'levels': [],
                        'employers': set()
                    }
                
                skill_data[skill]['frequency'] += 1
                if salary_avg:
                    skill_data[skill]['salaries'].append(salary_avg)
                if job.company_name:
                    skill_data[skill]['employers'].add(job.company_name)
                if hasattr(job, 'experience_level'):
                    skill_data[skill]['levels'].append(job.experience_level)
        
        # Calculate comprehensive skill metrics
        sorted_skills = []
        for skill, data in skill_data.items():
            importance_score = data['frequency'] / total_jobs
            avg_salary_impact = np.mean(data['salaries']) if data['salaries'] else 0
            employer_diversity = len(data['employers'])
            
            sorted_skills.append({
                'skill': skill,
                'importance': importance_score,
                'frequency': data['frequency'],
                'salary_impact': avg_salary_impact,
                'employer_count': employer_diversity,
                'common_level': max(set(data['levels']), key=data['levels'].count) if data['levels'] else 'Not specified',
                'market_demand_score': self._calculate_market_demand_score(
                    importance_score,
                    avg_salary_impact,
                    employer_diversity
                )
            })
        
        return sorted(sorted_skills, key=lambda x: x['market_demand_score'], reverse=True)
        
    def _calculate_market_demand_score(self, importance, salary_impact, employer_diversity):
        """Calculate a comprehensive market demand score for a skill"""
        # Normalize inputs
        norm_salary = min(salary_impact / 150000, 1)  # Assuming 150k as max salary impact
        norm_diversity = min(employer_diversity / 20, 1)  # Assuming 20 employers as max diversity
        
        # Weighted sum of factors
        weights = {
            'importance': 0.4,
            'salary': 0.35,
            'diversity': 0.25
        }
        
        score = (
            (importance * weights['importance']) +
            (norm_salary * weights['salary']) +
            (norm_diversity * weights['diversity'])
        )
        
        return round(score, 3)
    
    def _calculate_skill_gaps(self, current_skills, required_skills):
        """Calculate gaps between current and required skills"""
        gaps = []
        
        for req_skill in required_skills:
            skill_name = req_skill['skill']
            current_level = current_skills.get(skill_name, {}).get('proficiency', 0)
            
            if current_level < 3:  # Consider it a gap if proficiency is less than intermediate
                gap_size = 3 - current_level
                priority_score = self._calculate_priority_score(gap_size, req_skill)
                
                gaps.append({
                    'skill': skill_name,
                    'current_level': current_level,
                    'required_level': 3,
                    'gap_size': gap_size,
                    'importance': req_skill['importance'],
                    'salary_impact': req_skill['salary_impact'],
                    'priority_score': priority_score
                })
        
        return sorted(gaps, key=lambda x: x['priority_score'], reverse=True)
    
    def _calculate_priority_score(self, gap_size, requirements):
        """Calculate priority score for addressing a skill gap"""
        importance_weight = 0.4
        salary_weight = 0.3
        gap_weight = 0.3
        
        # Normalize salary impact to 0-1 scale
        max_salary_impact = 150000  # Adjust based on your data
        norm_salary_impact = min(requirements['salary_impact'] / max_salary_impact, 1)
        
        # Calculate priority score
        priority_score = (
            (requirements['importance'] * importance_weight) +
            (norm_salary_impact * salary_weight) +
            (gap_size/3 * gap_weight)  # Normalize gap size to 0-1 scale
        )
        
        return round(priority_score, 3)
    
    def _get_priority_skills(self, skill_gaps):
        """Get top priority skills for quick reference"""
        return [gap['skill'] for gap in skill_gaps[:3]]
        
    def _get_market_insights(self, target_role):
        """Get market insights for a target role"""
        jobs = JobOpportunity.query.filter(
            JobOpportunity.title.ilike(f"%{target_role}%")
        ).limit(100).all()

        if not jobs:
            return {
                'required_skills': {},
                'match_rate': 0,
                'avg_salary': 0,
                'demand_level': 'Low',
                'total_jobs': 0,
                'salary_range': {'min': 0, 'max': 0},
                'top_employers': [],
                'experience_levels': {},
                'location_distribution': {}
            }

        # Analyze job market data
        salaries = []
        employers = {}
        experience_levels = {}
        locations = {}
        total_jobs = len(jobs)

        for job in jobs:
            # Process salary data
            if job.salary_min and job.salary_max:
                salaries.append({
                    'min': job.salary_min,
                    'max': job.salary_max,
                    'avg': (job.salary_min + job.salary_max) / 2
                })

            # Process employer data
            if job.company_name:
                employers[job.company_name] = employers.get(job.company_name, 0) + 1

            # Process experience level
            if hasattr(job, 'experience_level'):
                experience_levels[job.experience_level] = experience_levels.get(job.experience_level, 0) + 1

            # Process location data
            if job.location:
                locations[job.location] = locations.get(job.location, 0) + 1

        # Calculate salary statistics
        if salaries:
            avg_salary = np.mean([s['avg'] for s in salaries])
            salary_range = {
                'min': min([s['min'] for s in salaries]),
                'max': max([s['max'] for s in salaries])
            }
        else:
            avg_salary = 0
            salary_range = {'min': 0, 'max': 0}

        # Process top employers
        top_employers = sorted(employers.items(), key=lambda x: x[1], reverse=True)[:5]
        top_employers = [{'name': emp[0], 'job_count': emp[1]} for emp in top_employers]

        # Determine demand level based on job count and trend
        if total_jobs > 50:
            demand_level = 'High'
        elif total_jobs > 20:
            demand_level = 'Medium'
        else:
            demand_level = 'Low'

        return {
            'total_jobs': total_jobs,
            'avg_salary': avg_salary,
            'salary_range': salary_range,
            'demand_level': demand_level,
            'top_employers': top_employers,
            'experience_levels': dict(sorted(experience_levels.items(), key=lambda x: x[1], reverse=True)),
            'location_distribution': dict(sorted(locations.items(), key=lambda x: x[1], reverse=True)[:5])
        }

    def _generate_skill_recommendations(self, skill_gaps, market_insights):
        """Generate personalized skill development recommendations"""
        if not skill_gaps:
            return [{
                'type': 'profile_update',
                'title': 'Complete Your Skill Profile',
                'description': 'Add your current skills to get personalized recommendations.',
                'priority': 'High',
                'timeline': 'Immediate',
                'action_items': [
                    'List your technical skills',
                    'Add proficiency levels',
                    'Specify your target role'
                ]
            }]

        recommendations = []
        
        # High-priority skill gaps
        top_gaps = skill_gaps[:3]
        for gap in top_gaps:
            recommendations.append({
                'type': 'skill_development',
                'title': f'Develop {gap["skill"]}',
                'description': f'Increase proficiency in {gap["skill"]} to enhance job prospects.',
                'priority': 'High',
                'timeline': 'Short-term',
                'metrics': {
                    'current_level': gap['current_level'],
                    'target_level': gap['required_level'],
                    'salary_impact': f"${gap['salary_impact']:,.2f}",
                    'market_demand': f"{gap['importance']*100:.0f}%"
                },
                'action_items': [
                    f'Take online courses in {gap["skill"]}',
                    f'Work on practice projects using {gap["skill"]}',
                    f'Join relevant technical communities'
                ]
            })

        # Market insight recommendations
        if market_insights['demand_level'] == 'High':
            recommendations.append({
                'type': 'market_insight',
                'title': 'High Market Demand',
                'description': 'Current job market shows strong demand for your target role.',
                'priority': 'Medium',
                'timeline': 'Ongoing',
                'metrics': {
                    'total_jobs': market_insights['total_jobs'],
                    'avg_salary': f"${market_insights['avg_salary']:,.2f}",
                    'top_employers': [emp['name'] for emp in market_insights['top_employers'][:3]]
                },
                'action_items': [
                    'Research top employers in your area',
                    'Tailor your resume for high-demand skills',
                    'Network with professionals in target companies'
                ]
            })

        # Salary optimization recommendation
        salary_range = market_insights.get('salary_range', {})
        if salary_range and salary_range['max'] > salary_range['min'] * 1.5:
            recommendations.append({
                'type': 'salary_optimization',
                'title': 'Salary Growth Potential',
                'description': 'Significant salary range for your target role based on skills and experience.',
                'priority': 'Medium',
                'timeline': 'Long-term',
                'metrics': {
                    'min_salary': f"${salary_range['min']:,.2f}",
                    'max_salary': f"${salary_range['max']:,.2f}",
                    'increase_potential': f"{((salary_range['max']/salary_range['min'])-1)*100:.0f}%"
                },
                'action_items': [
                    'Focus on high-impact skills',
                    'Gain relevant certifications',
                    'Build portfolio of complex projects'
                ]
            })

        # Location recommendation if there's significant geographical variation
        location_dist = market_insights.get('location_distribution', {})
        if len(location_dist) >= 3:
            top_locations = list(location_dist.items())[:3]
            recommendations.append({
                'type': 'location_insight',
                'title': 'Geographic Opportunities',
                'description': 'Consider job opportunities in high-demand locations.',
                'priority': 'Low',
                'timeline': 'Long-term',
                'metrics': {
                    'top_locations': [{'location': loc[0], 'job_count': loc[1]} for loc in top_locations]
                },
                'action_items': [
                    'Research cost of living in target locations',
                    'Explore remote work opportunities',
                    'Network with professionals in target locations'
                ]
            })

        return recommendations