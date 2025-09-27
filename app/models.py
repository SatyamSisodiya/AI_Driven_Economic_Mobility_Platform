from app import db
from datetime import datetime
import json

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    current_role = db.Column(db.String(200))
    experience_years = db.Column(db.Integer)
    education_level = db.Column(db.String(100))
    location = db.Column(db.String(200))
    target_role = db.Column(db.String(200))
    target_salary = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    skills = db.relationship('UserSkill', backref='user', lazy='dynamic')
    learning_paths = db.relationship('LearningPath', backref='user', lazy='dynamic')
    opportunities = db.relationship('UserOpportunity', backref='user', lazy='dynamic')

class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    category = db.Column(db.String(50))
    market_demand = db.Column(db.Float, default=0.0)  # 0-1 scale
    avg_salary_impact = db.Column(db.Integer, default=0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

class UserSkill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skill.id'), nullable=False)
    proficiency_level = db.Column(db.Integer, nullable=False)  # 1-5 scale
    verified = db.Column(db.Boolean, default=False)
    
    skill = db.relationship('Skill', backref='user_skills')

class LearningResource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    provider = db.Column(db.String(100))
    url = db.Column(db.String(500))
    skill_id = db.Column(db.Integer, db.ForeignKey('skill.id'))
    duration_hours = db.Column(db.Integer)
    cost = db.Column(db.Float, default=0.0)
    rating = db.Column(db.Float)
    difficulty_level = db.Column(db.String(20))  # beginner, intermediate, advanced

class LearningPath(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    estimated_duration_weeks = db.Column(db.Integer)
    progress = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='active')  # active, completed, paused
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class JobOpportunity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    company = db.Column(db.String(200))
    location = db.Column(db.String(200))
    salary_min = db.Column(db.Integer)
    salary_max = db.Column(db.Integer)
    description = db.Column(db.Text)
    requirements = db.Column(db.Text)  # JSON string
    url = db.Column(db.String(500))
    source = db.Column(db.String(100))
    posted_date = db.Column(db.DateTime)
    expires_date = db.Column(db.DateTime)
    remote_ok = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class UserOpportunity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    opportunity_id = db.Column(db.Integer, db.ForeignKey('job_opportunity.id'), nullable=False)
    match_score = db.Column(db.Float)
    status = db.Column(db.String(20), default='suggested')  # suggested, applied, interviewing, rejected, offered
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    opportunity = db.relationship('JobOpportunity')

class SkillGapAnalysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    target_role = db.Column(db.String(200))
    analysis_data = db.Column(db.Text)  # JSON string
    recommendations = db.Column(db.Text)  # JSON string
    priority_skills = db.Column(db.Text)  # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)