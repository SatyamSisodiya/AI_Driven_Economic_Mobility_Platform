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
        """Analyze job postings to determine required skills for a role"""
        # Get recent job postings for the role
        jobs = JobOpportunity.query.filter(
            JobOpportunity.title.ilike(f"%{target_role}%")
        ).limit(100).all()
        
        skill_frequency = {}
        skill_importance = {}
        total_jobs = len(jobs)
        
        for job in jobs:
            requirements = json.loads(job.requirements) if job.requirements else []
            salary_avg = (job.salary_min + job.salary_max) / 2 if job.salary_min and job.salary_max else None
            
            for skill in requirements:
                skill_frequency[skill] = skill_frequency.get(skill, 0) + 1
                if salary_avg:
                    if skill not in skill_importance:
                        skill_importance[skill] = []
                    skill_importance[skill].append(salary_avg)
        
        # Calculate skill importance scores
        sorted_skills = []
        for skill, freq in skill_frequency.items():
            importance_score = freq / total_jobs
            avg_salary_impact = np.mean(skill_importance.get(skill, [0]))
            
            sorted_skills.append({
                'skill': skill,
                'importance': importance_score,
                'frequency': freq,
                'salary_impact': avg_salary_impact
            })
        
        return sorted(sorted_skills, key=lambda x: x['importance'], reverse=True)
    
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