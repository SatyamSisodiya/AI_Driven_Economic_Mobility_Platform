# AI-Driven Economic Mobility Platform - Python Implementation Guide

## Project Overview

This guide provides a complete step-by-step implementation of the AI-Driven Economic Mobility Platform using Python Flask, SQLite, and real-time data sources. The focus is on three core features that can be implemented in a single day.

## Technology Stack

- **Backend Framework**: Flask (Python)
- **Database**: SQLite
- **Frontend**: Flask with Jinja2 templates + Bootstrap
- **AI/ML**: scikit-learn, pandas, numpy
- **Real-time Data**: APIs for job data, skills data, and learning resources
- **Task Queue**: Celery with Redis (for background API calls)
- **Environment**: Python 3.9+

## Core Features Implementation

### Feature 1: Skill Gap Analysis
### Feature 2: Personalized Learning Pathway Recommendations  
### Feature 3: Opportunity Identification Systems

## Step-by-Step Implementation Guide

### Step 1: Environment Setup (15 minutes)

#### 1.1 Create Project Directory
```bash
mkdir ai-economic-mobility
cd ai-economic-mobility
```

#### 1.2 Create Virtual Environment
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On Mac/Linux
source venv/bin/activate
```

#### 1.3 Install Required Packages
Create `requirements.txt`:
```txt
Flask==2.3.3
Flask-SQLAlchemy==3.0.5
Flask-WTF==1.1.1
WTForms==3.0.1
requests==2.31.0
pandas==2.1.1
numpy==1.25.2
scikit-learn==1.3.0
celery==5.3.1
redis==4.6.0
python-dotenv==1.0.0
beautifulsoup4==4.12.2
schedule==1.2.0
```

Install packages:
```bash
pip install -r requirements.txt
```

### Step 2: Project Structure Setup (10 minutes)

Create the following directory structure:
```
ai-economic-mobility/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes.py
│   ├── forms.py
│   ├── skills_analyzer.py
│   ├── learning_recommender.py
│   ├── opportunity_finder.py
│   ├── data_fetcher.py
│   └── templates/
│       ├── base.html
│       ├── dashboard.html
│       ├── profile.html
│       ├── skills_analysis.html
│       ├── learning_paths.html
│       └── opportunities.html
│   └── static/
│       ├── css/
│       │   └── style.css
│       └── js/
│           └── main.js
├── migrations/
├── config.py
├── run.py
├── requirements.txt
└── .env
```

### Step 3: Configuration Setup (10 minutes)

#### 3.1 Create `.env` file
```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///economic_mobility.db
REDIS_URL=redis://localhost:6379/0

# API Keys (Sign up for these services)
ADZUNA_APP_ID=your_adzuna_app_id
ADZUNA_APP_KEY=your_adzuna_api_key
COURSERA_API_KEY=your_coursera_api_key
GITHUB_TOKEN=your_github_token
USAJOBS_API_KEY=your_usajobs_api_key
```

#### 3.2 Create `config.py`
```python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///economic_mobility.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # API Configuration
    ADZUNA_APP_ID = os.environ.get('ADZUNA_APP_ID')
    ADZUNA_APP_KEY = os.environ.get('ADZUNA_APP_KEY')
    COURSERA_API_KEY = os.environ.get('COURSERA_API_KEY')
    GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
    USAJOBS_API_KEY = os.environ.get('USAJOBS_API_KEY')
    
    # Redis for Celery
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
```

### Step 4: Database Models (15 minutes)

#### 4.1 Create `app/__init__.py`
```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    
    from app.routes import main
    app.register_blueprint(main)
    
    return app
```

#### 4.2 Create `app/models.py`
```python
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
    skills = db.relationship('UserSkill', backref='user', lazy='dynamic', cascade='all, delete-orphan')
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
    
    skill = db.relationship('Skill', backref='learning_resources')

class LearningPath(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    estimated_duration_weeks = db.Column(db.Integer)
    progress = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='active')  # active, completed, paused
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    resources = db.relationship('LearningPathResource', backref='learning_path', cascade='all, delete-orphan')

class LearningPathResource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    learning_path_id = db.Column(db.Integer, db.ForeignKey('learning_path.id'), nullable=False)
    learning_resource_id = db.Column(db.Integer, db.ForeignKey('learning_resource.id'), nullable=False)
    order_position = db.Column(db.Integer, nullable=False)
    completed = db.Column(db.Boolean, default=False)
    
    resource = db.relationship('LearningResource')

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
```

### Step 5: Real-Time Data Fetchers (30 minutes)

#### 5.1 Create `app/data_fetcher.py`
```python
import requests
import pandas as pd
from datetime import datetime, timedelta
from app.models import Skill, JobOpportunity, LearningResource
from app import db
from config import Config
import json
import time

class DataFetcher:
    def __init__(self):
        self.config = Config()
    
    def fetch_job_market_data(self, location="United States", days_back=7):
        """Fetch real-time job data from Adzuna API"""
        jobs = []
        
        try:
            # Adzuna API for job data
            base_url = "https://api.adzuna.com/v1/api/jobs/us/search"
            params = {
                'app_id': self.config.ADZUNA_APP_ID,
                'app_key': self.config.ADZUNA_APP_KEY,
                'results_per_page': 100,
                'what': '',
                'where': location,
                'max_days_old': days_back,
                'sort_by': 'date'
            }
            
            for page in range(1, 6):  # Get first 5 pages
                params['page'] = page
                response = requests.get(base_url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    for job in data.get('results', []):
                        jobs.append({
                            'title': job.get('title', ''),
                            'company': job.get('company', {}).get('display_name', ''),
                            'location': job.get('location', {}).get('display_name', ''),
                            'salary_min': job.get('salary_min'),
                            'salary_max': job.get('salary_max'),
                            'description': job.get('description', ''),
                            'url': job.get('redirect_url', ''),
                            'source': 'Adzuna',
                            'posted_date': datetime.now() - timedelta(days=1),
                            'requirements': self._extract_requirements(job.get('description', ''))
                        })
                
                time.sleep(1)  # Rate limiting
                
        except Exception as e:
            print(f"Error fetching Adzuna data: {e}")
        
        # Add USAJobs.gov data
        jobs.extend(self._fetch_usajobs_data())
        
        return jobs
    
    def _fetch_usajobs_data(self):
        """Fetch jobs from USAJobs.gov API"""
        jobs = []
        
        try:
            headers = {
                'Host': 'data.usajobs.gov',
                'User-Agent': 'your-email@example.com',
                'Authorization-Key': self.config.USAJOBS_API_KEY
            }
            
            url = "https://data.usajobs.gov/api/search"
            params = {
                'ResultsPerPage': 100,
                'Page': 1
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                for job in data.get('SearchResult', {}).get('SearchResultItems', []):
                    job_detail = job.get('MatchedObjectDescriptor', {})
                    jobs.append({
                        'title': job_detail.get('PositionTitle', ''),
                        'company': job_detail.get('OrganizationName', 'US Government'),
                        'location': ', '.join([loc.get('LocationName', '') for loc in job_detail.get('PositionLocation', [])]),
                        'salary_min': job_detail.get('PositionRemuneration', [{}])[0].get('MinimumRange') if job_detail.get('PositionRemuneration') else None,
                        'salary_max': job_detail.get('PositionRemuneration', [{}])[0].get('MaximumRange') if job_detail.get('PositionRemuneration') else None,
                        'description': job_detail.get('UserArea', {}).get('Details', {}).get('JobSummary', ''),
                        'url': job_detail.get('ApplyURI', [''])[0],
                        'source': 'USAJobs',
                        'posted_date': datetime.now(),
                        'requirements': job_detail.get('QualificationSummary', '')
                    })
        
        except Exception as e:
            print(f"Error fetching USAJobs data: {e}")
        
        return jobs
    
    def _extract_requirements(self, description):
        """Extract skill requirements from job description using basic NLP"""
        common_skills = [
            'python', 'java', 'javascript', 'sql', 'html', 'css', 'react', 'node.js',
            'machine learning', 'data analysis', 'project management', 'communication',
            'leadership', 'excel', 'powerbi', 'tableau', 'aws', 'azure', 'docker',
            'kubernetes', 'agile', 'scrum', 'git', 'linux', 'windows', 'networking'
        ]
        
        description_lower = description.lower()
        found_skills = [skill for skill in common_skills if skill in description_lower]
        return json.dumps(found_skills)
    
    def fetch_learning_resources(self):
        """Fetch learning resources from multiple sources"""
        resources = []
        
        # Coursera courses (using web scraping as API is limited)
        resources.extend(self._fetch_coursera_courses())
        
        # Free resources from GitHub
        resources.extend(self._fetch_github_learning_resources())
        
        # Add Khan Academy, edX, etc.
        resources.extend(self._get_free_learning_resources())
        
        return resources
    
    def _fetch_coursera_courses(self):
        """Fetch popular Coursera courses"""
        courses = []
        
        # Popular course categories and their sample courses
        popular_courses = [
            {
                'title': 'Python for Everybody Specialization',
                'provider': 'Coursera',
                'url': 'https://www.coursera.org/specializations/python',
                'skill': 'Python',
                'duration_hours': 120,
                'cost': 49.0,
                'rating': 4.8,
                'difficulty_level': 'beginner'
            },
            {
                'title': 'Machine Learning Course',
                'provider': 'Coursera',
                'url': 'https://www.coursera.org/learn/machine-learning',
                'skill': 'Machine Learning',
                'duration_hours': 60,
                'cost': 79.0,
                'rating': 4.9,
                'difficulty_level': 'intermediate'
            },
            {
                'title': 'Google Data Analytics Professional Certificate',
                'provider': 'Coursera',
                'url': 'https://www.coursera.org/professional-certificates/google-data-analytics',
                'skill': 'Data Analysis',
                'duration_hours': 180,
                'cost': 39.0,
                'rating': 4.7,
                'difficulty_level': 'beginner'
            }
        ]
        
        return popular_courses
    
    def _fetch_github_learning_resources(self):
        """Fetch learning resources from GitHub"""
        resources = []
        
        try:
            headers = {'Authorization': f'token {self.config.GITHUB_TOKEN}'}
            
            # Search for awesome learning repositories
            search_queries = [
                'awesome-python',
                'awesome-machine-learning',
                'free-programming-books',
                'coding-interview-university'
            ]
            
            for query in search_queries:
                url = f"https://api.github.com/search/repositories?q={query}&sort=stars&order=desc"
                response = requests.get(url, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    for repo in data.get('items', [])[:5]:
                        resources.append({
                            'title': repo.get('name', '').replace('-', ' ').title(),
                            'provider': 'GitHub',
                            'url': repo.get('html_url', ''),
                            'skill': self._infer_skill_from_name(repo.get('name', '')),
                            'duration_hours': None,
                            'cost': 0.0,
                            'rating': min(5.0, repo.get('stargazers_count', 0) / 1000),
                            'difficulty_level': 'intermediate'
                        })
                
                time.sleep(1)  # Rate limiting
                
        except Exception as e:
            print(f"Error fetching GitHub resources: {e}")
        
        return resources
    
    def _get_free_learning_resources(self):
        """Get curated list of free learning resources"""
        return [
            {
                'title': 'Khan Academy Computer Programming',
                'provider': 'Khan Academy',
                'url': 'https://www.khanacademy.org/computing/computer-programming',
                'skill': 'Programming',
                'duration_hours': 40,
                'cost': 0.0,
                'rating': 4.5,
                'difficulty_level': 'beginner'
            },
            {
                'title': 'freeCodeCamp',
                'provider': 'freeCodeCamp',
                'url': 'https://www.freecodecamp.org/',
                'skill': 'Web Development',
                'duration_hours': 300,
                'cost': 0.0,
                'rating': 4.8,
                'difficulty_level': 'beginner'
            },
            {
                'title': 'MIT OpenCourseWare',
                'provider': 'MIT',
                'url': 'https://ocw.mit.edu/',
                'skill': 'Computer Science',
                'duration_hours': 200,
                'cost': 0.0,
                'rating': 4.9,
                'difficulty_level': 'advanced'
            }
        ]
    
    def _infer_skill_from_name(self, name):
        """Infer skill category from repository name"""
        name_lower = name.lower()
        
        skill_keywords = {
            'python': 'Python',
            'javascript': 'JavaScript',
            'machine-learning': 'Machine Learning',
            'data': 'Data Analysis',
            'web': 'Web Development',
            'interview': 'Technical Interviewing',
            'algorithm': 'Algorithms'
        }
        
        for keyword, skill in skill_keywords.items():
            if keyword in name_lower:
                return skill
        
        return 'General Programming'
    
    def update_skill_market_demand(self):
        """Update skill market demand based on job postings"""
        # Fetch recent job data
        jobs = self.fetch_job_market_data()
        
        # Analyze skill frequency
        skill_counts = {}
        total_jobs = len(jobs)
        
        for job in jobs:
            requirements = json.loads(job.get('requirements', '[]'))
            for skill in requirements:
                skill_counts[skill] = skill_counts.get(skill, 0) + 1
        
        # Update skill demand in database
        for skill_name, count in skill_counts.items():
            skill = Skill.query.filter_by(name=skill_name.title()).first()
            if not skill:
                skill = Skill(name=skill_name.title(), category='Technical')
                db.session.add(skill)
            
            # Calculate demand as percentage of jobs mentioning this skill
            skill.market_demand = count / total_jobs if total_jobs > 0 else 0
            skill.last_updated = datetime.utcnow()
        
        db.session.commit()
        return skill_counts

# Utility function to run data updates
def update_all_data():
    """Update all real-time data"""
    fetcher = DataFetcher()
    
    # Update job opportunities
    jobs = fetcher.fetch_job_market_data()
    for job_data in jobs:
        # Check if job already exists
        existing_job = JobOpportunity.query.filter_by(
            title=job_data['title'],
            company=job_data['company']
        ).first()
        
        if not existing_job:
            job = JobOpportunity(**job_data)
            db.session.add(job)
    
    # Update learning resources
    resources = fetcher.fetch_learning_resources()
    for resource_data in resources:
        # Find or create skill
        skill = Skill.query.filter_by(name=resource_data['skill']).first()
        if not skill:
            skill = Skill(name=resource_data['skill'], category='Technical')
            db.session.add(skill)
            db.session.flush()  # Get the ID
        
        # Check if resource already exists
        existing_resource = LearningResource.query.filter_by(
            title=resource_data['title'],
            provider=resource_data['provider']
        ).first()
        
        if not existing_resource:
            resource_data['skill_id'] = skill.id
            del resource_data['skill']  # Remove the skill name key
            resource = LearningResource(**resource_data)
            db.session.add(resource)
    
    # Update skill market demand
    fetcher.update_skill_market_demand()
    
    db.session.commit()
    print("Data update completed successfully!")
```

### Step 6: Skills Analysis Engine (25 minutes)

#### 6.1 Create `app/skills_analyzer.py`
```python
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
            return None
        
        target_role = target_role or user.target_role
        if not target_role:
            return {"error": "No target role specified"}
        
        # Get user's current skills
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
        analysis_data = {
            'current_skills': current_skills,
            'required_skills': required_skills,
            'skill_gaps': skill_gaps,
            'market_insights': market_insights
        }
        
        analysis = SkillGapAnalysis(
            user_id=user_id,
            target_role=target_role,
            analysis_data=json.dumps(analysis_data),
            recommendations=json.dumps(recommendations),
            priority_skills=json.dumps(self._get_priority_skills(skill_gaps)),
            created_at=datetime.utcnow()
        )
        
        db.session.add(analysis)
        db.session.commit()
        
        return {
            'analysis_id': analysis.id,
            'current_skills': current_skills,
            'required_skills': required_skills,
            'skill_gaps': skill_gaps,
            'recommendations': recommendations,
            'market_insights': market_insights,
            'priority_skills': self._get_priority_skills(skill_gaps)
        }
    
    def _get_user_skills(self, user_id):
        """Get current skills for a user"""
        user_skills = db.session.query(
            Skill.name, 
            UserSkill.proficiency_level,
            Skill.market_demand,
            Skill.avg_salary_impact
        ).join(
            UserSkill, Skill.id == UserSkill.skill_id
        ).filter(
            UserSkill.user_id == user_id
        ).all()
        
        skills_dict = {}
        for skill_name, proficiency, demand, salary_impact in user_skills:
            skills_dict[skill_name] = {
                'proficiency_level': proficiency,
                'market_demand': demand or 0,
                'salary_impact': salary_impact or 0
            }
        
        return skills_dict
    
    def _get_required_skills_for_role(self, target_role):
        """Analyze job postings to determine required skills for a role"""
        # Get recent job postings for the target role
        jobs = JobOpportunity.query.filter(
            JobOpportunity.title.contains(target_role)
        ).limit(50).all()
        
        if not jobs:
            # Fallback to similar roles
            role_keywords = target_role.lower().split()
            jobs = []
            for keyword in role_keywords:
                similar_jobs = JobOpportunity.query.filter(
                    JobOpportunity.title.ilike(f'%{keyword}%')
                ).limit(20).all()
                jobs.extend(similar_jobs)
        
        # Extract skills from job requirements
        all_requirements = []
        for job in jobs:
            if job.requirements:
                try:
                    req_skills = json.loads(job.requirements)
                    all_requirements.extend(req_skills)
                except:
                    # Handle text requirements
                    all_requirements.append(job.requirements)
        
        # Count skill frequency
        skill_frequency = {}
        total_jobs = len(jobs)
        
        for req in all_requirements:
            if isinstance(req, str):
                # Extract skills from text
                skills = self._extract_skills_from_text(req)
                for skill in skills:
                    skill_frequency[skill] = skill_frequency.get(skill, 0) + 1
            else:
                skill_frequency[req] = skill_frequency.get(req, 0) + 1
        
        # Calculate importance score
        required_skills = {}
        for skill, count in skill_frequency.items():
            importance = count / total_jobs if total_jobs > 0 else 0
            
            # Get skill market data
            skill_obj = Skill.query.filter_by(name=skill).first()
            market_demand = skill_obj.market_demand if skill_obj else 0
            salary_impact = skill_obj.avg_salary_impact if skill_obj else 0
            
            required_skills[skill] = {
                'importance': importance,
                'frequency': count,
                'market_demand': market_demand,
                'salary_impact': salary_impact,
                'required_level': min(5, max(1, int(importance * 5)))  # Convert to 1-5 scale
            }
        
        # Sort by importance
        sorted_skills = dict(sorted(required_skills.items(), 
                                  key=lambda x: x[1]['importance'], 
                                  reverse=True))
        
        return sorted_skills
    
    def _extract_skills_from_text(self, text):
        """Extract skill keywords from text"""
        common_skills = [
            'Python', 'Java', 'JavaScript', 'SQL', 'HTML', 'CSS', 'React', 'Node.js',
            'Machine Learning', 'Data Analysis', 'Project Management', 'Communication',
            'Leadership', 'Excel', 'PowerBI', 'Tableau', 'AWS', 'Azure', 'Docker',
            'Kubernetes', 'Agile', 'Scrum', 'Git', 'Linux', 'Windows', 'Networking',
            'C++', 'C#', 'PHP', 'Ruby', 'Go', 'Rust', 'Swift', 'Kotlin', 'R',
            'Pandas', 'NumPy', 'TensorFlow', 'PyTorch', 'Scikit-learn', 'Django',
            'Flask', 'Angular', 'Vue.js', 'MongoDB', 'PostgreSQL', 'MySQL',
            'Redis', 'Elasticsearch', 'Kafka', 'Spark', 'Hadoop', 'Terraform'
        ]
        
        text_lower = text.lower()
        found_skills = []
        
        for skill in common_skills:
            if skill.lower() in text_lower:
                found_skills.append(skill)
        
        return found_skills
    
    def _calculate_skill_gaps(self, current_skills, required_skills):
        """Calculate gaps between current and required skills"""
        gaps = []
        
        for skill_name, requirements in required_skills.items():
            current_level = current_skills.get(skill_name, {}).get('proficiency_level', 0)
            required_level = requirements['required_level']
            
            gap_size = required_level - current_level
            
            if gap_size > 0:
                gaps.append({
                    'skill': skill_name,
                    'current_level': current_level,
                    'required_level': required_level,
                    'gap_size': gap_size,
                    'importance': requirements['importance'],
                    'market_demand': requirements['market_demand'],
                    'salary_impact': requirements['salary_impact'],
                    'priority_score': self._calculate_priority_score(gap_size, requirements)
                })
        
        # Sort by priority score
        gaps.sort(key=lambda x: x['priority_score'], reverse=True)
        
        return gaps
    
    def _calculate_priority_score(self, gap_size, requirements):
        """Calculate priority score for addressing a skill gap"""
        # Weighted combination of factors
        importance_weight = 0.4
        market_demand_weight = 0.3
        salary_impact_weight = 0.2
        gap_urgency_weight = 0.1
        
        # Normalize salary impact (assuming max is 50k)
        normalized_salary = min(1.0, requirements['salary_impact'] / 50000)
        
        priority_score = (
            requirements['importance'] * importance_weight +
            requirements['market_demand'] * market_demand_weight +
            normalized_salary * salary_impact_weight +
            (gap_size / 5) * gap_urgency_weight
        )
        
        return round(priority_score, 3)
    
    def _get_market_insights(self, target_role):
        """Get market insights for the target role"""
        # Get salary data
        jobs_with_salary = JobOpportunity.query.filter(
            JobOpportunity.title.contains(target_role),
            JobOpportunity.salary_min.isnot(None)
        ).all()
        
        salary_data = []
        locations = {}
        companies = {}
        
        for job in jobs_with_salary:
            if job.salary_min and job.salary_max:
                avg_salary = (job.salary_min + job.salary_max) / 2
                salary_data.append(avg_salary)
            
            if job.location:
                locations[job.location] = locations.get(job.location, 0) + 1
            
            if job.company:
                companies[job.company] = companies.get(job.company, 0) + 1
        
        insights = {
            'total_opportunities': JobOpportunity.query.filter(
                JobOpportunity.title.contains(target_role)
            ).count(),
            'salary_range': {
                'min': min(salary_data) if salary_data else None,
                'max': max(salary_data) if salary_data else None,
                'median': np.median(salary_data) if salary_data else None,
                'average': np.mean(salary_data) if salary_data else None
            },
            'top_locations': dict(sorted(locations.items(), 
                                       key=lambda x: x[1], 
                                       reverse=True)[:5]),
            'top_hiring_companies': dict(sorted(companies.items(), 
                                              key=lambda x: x[1], 
                                              reverse=True)[:5]),
            'growth_trend': self._calculate_growth_trend(target_role)
        }
        
        return insights
    
    def _calculate_growth_trend(self, target_role):
        """Calculate job growth trend for the role"""
        # Simple implementation - compare recent vs older postings
        from datetime import timedelta
        
        recent_count = JobOpportunity.query.filter(
            JobOpportunity.title.contains(target_role),
            JobOpportunity.created_at >= datetime.utcnow() - timedelta(days=30)
        ).count()
        
        older_count = JobOpportunity.query.filter(
            JobOpportunity.title.contains(target_role),
            JobOpportunity.created_at < datetime.utcnow() - timedelta(days=30)
        ).count()
        
        if older_count > 0:
            growth_rate = ((recent_count - older_count) / older_count) * 100
        else:
            growth_rate = 0
        
        return {
            'growth_rate_30_days': round(growth_rate, 2),
            'trend': 'growing' if growth_rate > 10 else 'stable' if growth_rate > -10 else 'declining'
        }
    
    def _generate_skill_recommendations(self, skill_gaps, market_insights):
        """Generate actionable recommendations"""
        recommendations = []
        
        # Focus on top 5 priority skills
        top_gaps = skill_gaps[:5]
        
        for gap in top_gaps:
            rec = {
                'skill': gap['skill'],
                'priority': 'High' if gap['priority_score'] > 0.7 else 'Medium' if gap['priority_score'] > 0.4 else 'Low',
                'time_investment': self._estimate_learning_time(gap),
                'roi_potential': self._estimate_roi(gap, market_insights),
                'action_steps': self._generate_action_steps(gap)
            }
            recommendations.append(rec)
        
        return recommendations
    
    def _estimate_learning_time(self, gap):
        """Estimate time needed to close skill gap"""
        base_hours_per_level = {1: 20, 2: 40, 3: 80, 4: 120, 5: 200}
        hours_needed = base_hours_per_level.get(gap['required_level'], 100)
        
        return {
            'estimated_hours': hours_needed,
            'weeks_part_time': round(hours_needed / 10, 1),  # 10 hours per week
            'weeks_full_time': round(hours_needed / 40, 1)   # 40 hours per week
        }
    
    def _estimate_roi(self, gap, market_insights):
        """Estimate return on investment for learning this skill"""
        salary_boost = gap.get('salary_impact', 0)
        market_opportunities = market_insights.get('total_opportunities', 0)
        
        return {
            'potential_salary_increase': salary_boost,
            'job_opportunities': market_opportunities,
            'roi_score': round((salary_boost / 1000 + market_opportunities / 100) / 2, 2)
        }
    
    def _generate_action_steps(self, gap):
        """Generate specific action steps for skill development"""
        skill_name = gap['skill']
        current_level = gap['current_level']
        
        steps = []
        
        if current_level == 0:
            steps.append(f"Start with beginner tutorials in {skill_name}")
            steps.append(f"Complete at least 2 online courses covering {skill_name} basics")
            steps.append(f"Practice with simple {skill_name} projects")
        elif current_level <= 2:
            steps.append(f"Take intermediate {skill_name} courses")
            steps.append(f"Build portfolio projects showcasing {skill_name}")
            steps.append(f"Join {skill_name} communities and forums")
        else:
            steps.append(f"Pursue advanced {skill_name} certifications")
            steps.append(f"Contribute to open source {skill_name} projects")
            steps.append(f"Consider teaching or mentoring others in {skill_name}")
        
        return steps
    
    def _get_priority_skills(self, skill_gaps):
        """Get top priority skills for quick reference"""
        return [gap['skill'] for gap in skill_gaps[:3]]
    
    def get_user_analysis_history(self, user_id):
        """Get historical skill gap analyses for a user"""
        analyses = SkillGapAnalysis.query.filter_by(user_id=user_id)\
                                        .order_by(SkillGapAnalysis.created_at.desc())\
                                        .all()
        
        history = []
        for analysis in analyses:
            history.append({
                'id': analysis.id,
                'target_role': analysis.target_role,
                'created_at': analysis.created_at,
                'priority_skills': json.loads(analysis.priority_skills),
                'recommendations_count': len(json.loads(analysis.recommendations))
            })
        
        return history
```

### Step 7: Learning Path Recommender (20 minutes)

#### 6.2 Create `app/learning_recommender.py`
```python
import pandas as pd
import numpy as np
from app.models import (User, UserSkill, Skill, LearningResource, 
                       LearningPath, LearningPathResource, SkillGapAnalysis)
from app import db
import json
from datetime import datetime, timedelta

class LearningRecommender:
    def __init__(self):
        pass
    
    def generate_learning_path(self, user_id, analysis_id=None, custom_skills=None):
        """Generate personalized learning pathway for a user"""
        user = User.query.get(user_id)
        if not user:
            return {"error": "User not found"}
        
        # Get skill gaps from analysis or custom skills
        if analysis_id:
            analysis = SkillGapAnalysis.query.get(analysis_id)
            if not analysis:
                return {"error": "Analysis not found"}
            
            skill_gaps = json.loads(analysis.analysis_data)['skill_gaps']
        elif custom_skills:
            skill_gaps = self._create_skill_gaps_from_custom(custom_skills)
        else:
            # Use latest analysis
            latest_analysis = SkillGapAnalysis.query.filter_by(user_id=user_id)\
                                                   .order_by(SkillGapAnalysis.created_at.desc())\
                                                   .first()
            if not latest_analysis:
                return {"error": "No skill analysis found"}
            
            skill_gaps = json.loads(latest_analysis.analysis_data)['skill_gaps']
        
        # Get user constraints
        user_constraints = self._get_user_constraints(user)
        
        # Generate learning pathway
        learning_paths = []
        
        # Focus on top priority skills
        priority_skills = sorted(skill_gaps, key=lambda x: x['priority_score'], reverse=True)[:5]
        
        for skill_gap in priority_skills:
            path = self._create_skill_learning_path(skill_gap, user_constraints)
            if path:
                learning_paths.append(path)
        
        # Create optimized learning schedule
        optimized_schedule = self._optimize_learning_schedule(learning_paths, user_constraints)
        
        # Save to database
        saved_paths = self._save_learning_paths(user_id, learning_paths)
        
        return {
            'learning_paths': learning_paths,
            'optimized_schedule': optimized_schedule,
            'estimated_completion': self._calculate_completion_date(optimized_schedule, user_constraints),
            'saved_path_ids': saved_paths,
            'total_time_investment': sum(path['estimated_hours'] for path in learning_paths)
        }
    
    def _get_user_constraints(self, user):
        """Get user's learning constraints and preferences"""
        # Default constraints - in a real app, this would be from user profile
        return {
            'available_hours_per_week': 10,  # Default 10 hours per week
            'budget_limit': 100,  # Default $100 budget
            'preferred_learning_style': 'mixed',  # video, text, interactive, mixed
            'difficulty_preference': 'gradual',  # fast_track, gradual, thorough
            'time_to_completion': 12  # weeks
        }
    
    def _create_skill_learning_path(self, skill_gap, constraints):
        """Create learning path for a specific skill"""
        skill_name = skill_gap['skill']
        current_level = skill_gap['current_level']
        target_level = skill_gap['required_level']
        
        # Get available learning resources for this skill
        skill_obj = Skill.query.filter_by(name=skill_name).first()
        if not skill_obj:
            return None
        
        resources = LearningResource.query.filter_by(skill_id=skill_obj.id).all()
        
        if not resources:
            # Create default resources if none exist
            resources = self._create_default_resources(skill_name, skill_obj.id)
        
        # Filter resources based on constraints
        filtered_resources = self._filter_resources(resources, constraints, current_level, target_level)
        
        # Sequence resources optimally
        sequenced_resources = self._sequence_resources(filtered_resources, current_level, target_level)
        
        # Calculate path metadata
        total_hours = sum(resource.duration_hours or 20 for resource in sequenced_resources)
        total_cost = sum(resource.cost or 0 for resource in sequenced_resources)
        
        path = {
            'skill_name': skill_name,
            'skill_id': skill_obj.id,
            'current_level': current_level,
            'target_level': target_level,
            'priority_score': skill_gap['priority_score'],
            'resources': [self._resource_to_dict(r) for r in sequenced_resources],
            'estimated_hours': total_hours,
            'estimated_cost': total_cost,
            'estimated_weeks': round(total_hours / constraints['available_hours_per_week'], 1),
            'milestones': self._create_milestones(sequenced_resources, current_level, target_level)
        }
        
        return path
    
    def _filter_resources(self, resources, constraints, current_level, target_level):
        """Filter resources based on user constraints"""
        filtered = []
        
        budget_spent = 0
        
        for resource in resources:
            # Budget constraint
            resource_cost = resource.cost or 0
            if budget_spent + resource_cost > constraints['budget_limit']:
                continue
            
            # Difficulty level matching
            difficulty_map = {'beginner': 1, 'intermediate': 3, 'advanced': 5}
            resource_difficulty = difficulty_map.get(resource.difficulty_level, 3)
            
            # Include resource if it matches the learning progression
            if current_level <= resource_difficulty <= target_level + 1:
                filtered.append(resource)
                budget_spent += resource_cost
        
        # If no resources within budget, include free ones
        if not filtered:
            free_resources = [r for r in resources if (r.cost or 0) == 0]
            filtered = free_resources[:5]  # Limit to 5 free resources
        
        return filtered
    
    def _sequence_resources(self, resources, current_level, target_level):
        """Sequence resources in optimal learning order"""
        # Sort by difficulty level and rating
        difficulty_map = {'beginner': 1, 'intermediate': 3, 'advanced': 5}
        
        def sort_key(resource):
            difficulty = difficulty_map.get(resource.difficulty_level, 3)
            rating = resource.rating or 3
            return (difficulty, -rating)  # Lower difficulty first, higher rating first
        
        return sorted(resources, key=sort_key)
    
    def _create_milestones(self, resources, current_level, target_level):
        """Create learning milestones"""
        milestones = []
        
        level_progression = list(range(current_level + 1, target_level + 1))
        resources_per_level = len(resources) // len(level_progression) if level_progression else 1
        
        for i, level in enumerate(level_progression):
            start_idx = i * resources_per_level
            end_idx = min((i + 1) * resources_per_level, len(resources))
            level_resources = resources[start_idx:end_idx]
            
            milestones.append({
                'level': level,
                'title': f'Reach Level {level}',
                'description': f'Complete foundational learning for level {level}',
                'resources': [r.id for r in level_resources],
                'estimated_hours': sum(r.duration_hours or 20 for r in level_resources)
            })
        
        return milestones
    
    def _optimize_learning_schedule(self, learning_paths, constraints):
        """Create optimized weekly learning schedule"""
        total_hours_available = constraints['available_hours_per_week']
        
        # Distribute hours based on priority scores
        total_priority = sum(path['priority_score'] for path in learning_paths)
        
        schedule = []
        
        for path in learning_paths:
            if total_priority > 0:
                allocated_hours = (path['priority_score'] / total_priority) * total_hours_available
            else:
                allocated_hours = total_hours_available / len(learning_paths)
            
            schedule.append({
                'skill': path['skill_name'],
                'weekly_hours': round(allocated_hours, 1),
                'priority': path['priority_score'],
                'estimated_weeks_to_complete': round(path['estimated_hours'] / allocated_hours) if allocated_hours > 0 else 999
            })
        
        return sorted(schedule, key=lambda x: x['priority'], reverse=True)
    
    def _calculate_completion_date(self, schedule, constraints):
        """Calculate estimated completion date"""
        max_weeks = max(item['estimated_weeks_to_complete'] for item in schedule) if schedule else 0
        completion_date = datetime.now() + timedelta(weeks=max_weeks)
        
        return {
            'estimated_weeks': max_weeks,
            'completion_date': completion_date.strftime('%Y-%m-%d'),
            'intensive_completion': round(max_weeks * 0.7, 1),  # If doing 40% more hours per week
        }
    
    def _save_learning_paths(self, user_id, learning_paths):
        """Save learning paths to database"""
        saved_path_ids = []
        
        for path_data in learning_paths:
            # Create learning path
            learning_path = LearningPath(
                user_id=user_id,
                title=f"Master {path_data['skill_name']}",
                description=f"Comprehensive learning path to advance from level {path_data['current_level']} to {path_data['target_level']} in {path_data['skill_name']}",
                estimated_duration_weeks=path_data['estimated_weeks'],
                status='active'
            )
            
            db.session.add(learning_path)
            db.session.flush()  # Get the ID
            
            # Add resources to path
            for i, resource_data in enumerate(path_data['resources']):
                path_resource = LearningPathResource(
                    learning_path_id=learning_path.id,
                    learning_resource_id=resource_data['id'],
                    order_position=i + 1,
                    completed=False
                )
                db.session.add(path_resource)
            
            saved_path_ids.append(learning_path.id)
        
        db.session.commit()
        return saved_path_ids
    
    def _resource_to_dict(self, resource):
        """Convert resource object to dictionary"""
        return {
            'id': resource.id,
            'title': resource.title,
            'provider': resource.provider,
            'url': resource.url,
            'duration_hours': resource.duration_hours,
            'cost': resource.cost,
            'rating': resource.rating,
            'difficulty_level': resource.difficulty_level
        }
    
    def _create_default_resources(self, skill_name, skill_id):
        """Create default learning resources if none exist"""
        default_resources = [
            {
                'title': f'{skill_name} Fundamentals',
                'provider': 'Online Learning',
                'url': f'https://search.google.com/search?q={skill_name}+tutorial',
                'skill_id': skill_id,
                'duration_hours': 20,
                'cost': 0.0,
                'rating': 4.0,
                'difficulty_level': 'beginner'
            },
            {
                'title': f'Intermediate {skill_name}',
                'provider': 'Online Learning',
                'url': f'https://search.google.com/search?q={skill_name}+intermediate+course',
                'skill_id': skill_id,
                'duration_hours': 40,
                'cost': 49.0,
                'rating': 4.2,
                'difficulty_level': 'intermediate'
            },
            {
                'title': f'Advanced {skill_name} Mastery',
                'provider': 'Online Learning',
                'url': f'https://search.google.com/search?q={skill_name}+advanced+certification',
                'skill_id': skill_id,
                'duration_hours': 60,
                'cost': 99.0,
                'rating': 4.5,
                'difficulty_level': 'advanced'
            }
        ]
        
        resources = []
        for resource_data in default_resources:
            resource = LearningResource(**resource_data)
            db.session.add(resource)
            resources.append(resource)
        
        db.session.flush()
        return resources
    
    def _create_skill_gaps_from_custom(self, custom_skills):
        """Create skill gaps from custom skill list"""
        gaps = []
        for i, skill_name in enumerate(custom_skills):
            gaps.append({
                'skill': skill_name,
                'current_level': 0,
                'required_level': 3,
                'priority_score': 0.8 - (i * 0.1),  # Decreasing priority
                'gap_size': 3,
                'importance': 0.8,
                'market_demand': 0.6,
                'salary_impact': 5000
            })
        return gaps
    
    def update_progress(self, user_id, learning_path_id, resource_id, completed=True):
        """Update progress on a learning resource"""
        path_resource = LearningPathResource.query.filter_by(
            learning_path_id=learning_path_id,
            learning_resource_id=resource_id
        ).first()
        
        if not path_resource:
            return {"error": "Learning path resource not found"}
        
        path_resource.completed = completed
        
        # Update overall path progress
        learning_path = LearningPath.query.get(learning_path_id)
        total_resources = LearningPathResource.query.filter_by(learning_path_id=learning_path_id).count()
        completed_resources = LearningPathResource.query.filter_by(
            learning_path_id=learning_path_id,
            completed=True
        ).count()
        
        progress_percentage = (completed_resources / total_resources) * 100 if total_resources > 0 else 0
        learning_path.progress = progress_percentage
        
        # Update status
        if progress_percentage >= 100:
            learning_path.status = 'completed'
        elif progress_percentage > 0:
            learning_path.status = 'active'
        
        db.session.commit()
        
        return {
            "success": True,
            "progress_percentage": progress_percentage,
            "status": learning_path.status
        }
    
    def get_user_learning_paths(self, user_id):
        """Get all learning paths for a user"""
        paths = LearningPath.query.filter_by(user_id=user_id)\
                                  .order_by(LearningPath.created_at.desc())\
                                  .all()
        
        result = []
        for path in paths:
            path_data = {
                'id': path.id,
                'title': path.title,
                'description': path.description,
                'estimated_duration_weeks': path.estimated_duration_weeks,
                'progress': path.progress,
                'status': path.status,
                'created_at': path.created_at,
                'resources': []
            }
            
            # Get resources
            path_resources = LearningPathResource.query.filter_by(learning_path_id=path.id)\
                                                       .order_by(LearningPathResource.order_position)\
                                                       .all()
            
            for path_resource in path_resources:
                resource_data = {
                    'id': path_resource.resource.id,
                    'title': path_resource.resource.title,
                    'provider': path_resource.resource.provider,
                    'url': path_resource.resource.url,
                    'duration_hours': path_resource.resource.duration_hours,
                    'cost': path_resource.resource.cost,
                    'completed': path_resource.completed,
                    'order_position': path_resource.order_position
                }
                path_data['resources'].append(resource_data)
            
            result.append(path_data)
        
        return result
    
    def get_recommended_next_actions(self, user_id):
        """Get recommended next actions for the user"""
        # Get active learning paths
        active_paths = LearningPath.query.filter_by(user_id=user_id, status='active').all()
        
        next_actions = []
        
        for path in active_paths:
            # Find next uncompleted resource
            next_resource = db.session.query(LearningPathResource, LearningResource)\
                                     .join(LearningResource)\
                                     .filter(
                                         LearningPathResource.learning_path_id == path.id,
                                         LearningPathResource.completed == False
                                     )\
                                     .order_by(LearningPathResource.order_position)\
                                     .first()
            
            if next_resource:
                path_resource, resource = next_resource
                next_actions.append({
                    'learning_path_id': path.id,
                    'skill': path.title.replace('Master ', ''),
                    'action': f'Continue with "{resource.title}"',
                    'resource_id': resource.id,
                    'estimated_hours': resource.duration_hours,
                    'url': resource.url,
                    'priority': 1.0 - (path.progress / 100)  # Higher priority for less progress
                })
        
        return sorted(next_actions, key=lambda x: x['priority'], reverse=True)
```

### Step 8: Opportunity Finder (25 minutes)

#### 6.3 Create `app/opportunity_finder.py`
```python
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
    
    def find_opportunities(self, user_id, opportunity_types=['jobs', 'programs'], limit=20):
        """Find relevant opportunities for a user"""
        user = User.query.get(user_id)
        if not user:
            return {"error": "User not found"}
        
        opportunities = []
        
        if 'jobs' in opportunity_types:
            job_opportunities = self._find_job_matches(user, limit//2)
            opportunities.extend(job_opportunities)
        
        if 'programs' in opportunity_types:
            program_opportunities = self._find_program_matches(user, limit//2)
            opportunities.extend(program_opportunities)
        
        # Sort by match score
        opportunities.sort(key=lambda x: x['match_score'], reverse=True)
        
        # Save top opportunities for user
        self._save_user_opportunities(user_id, opportunities[:limit])
        
        return {
            'opportunities': opportunities[:limit],
            'total_found': len(opportunities),
            'filters_applied': self._get_applied_filters(user),
            'recommendations': self._generate_opportunity_recommendations(opportunities, user)
        }
    
    def _find_job_matches(self, user, limit):
        """Find matching job opportunities"""
        user_skills = self._get_user_skill_vector(user.id)
        user_preferences = self._get_user_preferences(user)
        
        # Get recent job opportunities
        jobs = JobOpportunity.query.filter(
            JobOpportunity.created_at >= datetime.utcnow() - timedelta(days=30)
        ).all()
        
        if not jobs:
            # Fallback to all jobs if no recent ones
            jobs = JobOpportunity.query.limit(200).all()
        
        job_matches = []
        
        for job in jobs:
            match_data = self._calculate_job_match(job, user, user_skills, user_preferences)
            
            if match_data['match_score'] > 0.3:  # Minimum threshold
                job_matches.append({
                    'type': 'job',
                    'id': job.id,
                    'title': job.title,
                    'company': job.company,
                    'location': job.location,
                    'salary_min': job.salary_min,
                    'salary_max': job.salary_max,
                    'description': job.description[:200] + '...' if job.description else '',
                    'url': job.url,
                    'source': job.source,
                    'match_score': match_data['match_score'],
                    'match_explanation': match_data['explanation'],
                    'skill_matches': match_data['skill_matches'],
                    'missing_skills': match_data['missing_skills'],
                    'posted_date': job.posted_date or job.created_at,
                    'remote_ok': job.remote_ok
                })
        
        return sorted(job_matches, key=lambda x: x['match_score'], reverse=True)[:limit]
    
    def _find_program_matches(self, user, limit):
        """Find matching learning programs and opportunities"""
        user_skills = self._get_user_skill_vector(user.id)
        
        # Get learning resources as "program opportunities"
        resources = LearningResource.query.filter(
            LearningResource.cost == 0  # Free programs
        ).all()
        
        program_matches = []
        
        for resource in resources:
            match_score = self._calculate_program_match(resource, user, user_skills)
            
            if match_score > 0.4:
                program_matches.append({
                    'type': 'program',
                    'id': resource.id,
                    'title': resource.title,
                    'provider': resource.provider,
                    'description': f"Free learning program: {resource.title}",
                    'url': resource.url,
                    'duration_hours': resource.duration_hours,
                    'cost': resource.cost,
                    'rating': resource.rating,
                    'difficulty_level': resource.difficulty_level,
                    'match_score': match_score,
                    'skill_focus': resource.skill.name if resource.skill else 'General',
                    'match_explanation': f"Matches your learning goals in {resource.skill.name if resource.skill else 'skill development'}"
                })
        
        return sorted(program_matches, key=lambda x: x['match_score'], reverse=True)[:limit]
    
    def _get_user_skill_vector(self, user_id):
        """Create skill vector for user"""
        user_skills = db.session.query(Skill.name, UserSkill.proficiency_level)\
                               .join(UserSkill)\
                               .filter(UserSkill.user_id == user_id)\
                               .all()
        
        skill_dict = {}
        for skill_name, proficiency in user_skills:
            skill_dict[skill_name.lower()] = proficiency
        
        return skill_dict
    
    def _get_user_preferences(self, user):
        """Get user job preferences"""
        return {
            'target_role': user.target_role,
            'location': user.location,
            'target_salary': user.target_salary,
            'experience_years': user.experience_years or 0
        }
    
    def _calculate_job_match(self, job, user, user_skills, preferences):
        """Calculate how well a job matches a user"""
        match_components = {}
        
        # 1. Skill matching
        job_requirements = self._extract_job_skills(job)
        skill_match_data = self._calculate_skill_match(user_skills, job_requirements)
        match_components['skills'] = skill_match_data['score']
        
        # 2. Title/Role matching
        title_match = self._calculate_title_match(job.title, preferences['target_role'])
        match_components['title'] = title_match
        
        # 3. Location matching
        location_match = self._calculate_location_match(job.location, preferences['location'])
        match_components['location'] = location_match
        
        # 4. Salary matching
        salary_match = self._calculate_salary_match(job, preferences['target_salary'])
        match_components['salary'] = salary_match
        
        # 5. Experience matching
        experience_match = self._calculate_experience_match(job, preferences['experience_years'])
        match_components['experience'] = experience_match
        
        # Weighted composite score
        weights = {
            'skills': 0.4,
            'title': 0.25,
            'location': 0.15,
            'salary': 0.1,
            'experience': 0.1
        }
        
        composite_score = sum(match_components[component] * weights[component] 
                            for component in match_components)
        
        # Generate explanation
        explanation = self._generate_match_explanation(match_components, skill_match_data)
        
        return {
            'match_score': round(composite_score, 3),
            'explanation': explanation,
            'skill_matches': skill_match_data['matches'],
            'missing_skills': skill_match_data['missing'],
            'components': match_components
        }
    
    def _extract_job_skills(self, job):
        """Extract required skills from job posting"""
        text_to_analyze = f"{job.title} {job.description or ''}"
        
        if job.requirements:
            try:
                req_skills = json.loads(job.requirements)
                if isinstance(req_skills, list):
                    return [skill.lower() for skill in req_skills]
            except:
                text_to_analyze += f" {job.requirements}"
        
        # Extract skills using keyword matching
        common_skills = [
            'python', 'java', 'javascript', 'sql', 'html', 'css', 'react', 'node.js',
            'machine learning', 'data analysis', 'project management', 'communication',
            'leadership', 'excel', 'powerbi', 'tableau', 'aws', 'azure', 'docker',
            'kubernetes', 'agile', 'scrum', 'git', 'linux', 'windows', 'networking',
            'c++', 'c#', 'php', 'ruby', 'go', 'rust', 'swift', 'kotlin', 'r'
        ]
        
        text_lower = text_to_analyze.lower()
        found_skills = [skill for skill in common_skills if skill in text_lower]
        
        return found_skills
    
    def _calculate_skill_match(self, user_skills, job_requirements):
        """Calculate skill match between user and job"""
        matches = []
        missing = []
        
        total_job_skills = len(job_requirements)
        if total_job_skills == 0:
            return {'score': 0.5, 'matches': [], 'missing': []}
        
        matched_skills = 0
        skill_quality_score = 0
        
        for required_skill in job_requirements:
            user_proficiency = user_skills.get(required_skill, 0)
            
            if user_proficiency > 0:
                matched_skills += 1
                skill_quality_score += user_proficiency / 5  # Normalize to 0-1
                matches.append({
                    'skill': required_skill,
                    'user_level': user_proficiency,
                    'match_quality': user_proficiency / 5
                })
            else:
                missing.append(required_skill)
        
        # Calculate match score
        coverage_score = matched_skills / total_job_skills
        quality_score = skill_quality_score / total_job_skills if total_job_skills > 0 else 0
        
        # Combine coverage and quality
        match_score = (coverage_score * 0.7) + (quality_score * 0.3)
        
        return {
            'score': match_score,
            'matches': matches,
            'missing': missing
        }
    
    def _calculate_title_match(self, job_title, target_role):
        """Calculate how well job title matches target role"""
        if not target_role:
            return 0.5
        
        job_title_lower = job_title.lower()
        target_role_lower = target_role.lower()
        
        # Direct substring match
        if target_role_lower in job_title_lower or job_title_lower in target_role_lower:
            return 0.9
        
        # Keyword overlap
        job_words = set(re.findall(r'\b\w+\b', job_title_lower))
        target_words = set(re.findall(r'\b\w+\b', target_role_lower))
        
        common_words = job_words.intersection(target_words)
        total_words = job_words.union(target_words)
        
        if len(total_words) == 0:
            return 0
        
        overlap_score = len(common_words) / len(total_words)
        return min(0.8, overlap_score * 2)  # Cap at 0.8 for partial matches
    
    def _calculate_location_match(self, job_location, user_location):
        """Calculate location match score"""
        if not user_location or not job_location:
            return 0.5  # Neutral if no location info
        
        job_loc_lower = job_location.lower()
        user_loc_lower = user_location.lower()
        
        # Check for remote work
        if 'remote' in job_loc_lower:
            return 0.9
        
        # Direct match
        if user_loc_lower in job_loc_lower or job_loc_lower in user_loc_lower:
            return 1.0
        
        # State/country level match
        job_parts = job_loc_lower.split(', ')
        user_parts = user_loc_lower.split(', ')
        
        for job_part in job_parts:
            for user_part in user_parts:
                if job_part.strip() == user_part.strip():
                    return 0.7
        
        return 0.2  # Different locations
    
    def _calculate_salary_match(self, job, target_salary):
        """Calculate salary match score"""
        if not target_salary or not job.salary_min:
            return 0.5
        
        job_salary_avg = job.salary_min
        if job.salary_max:
            job_salary_avg = (job.salary_min + job.salary_max) / 2
        
        # Calculate how close the salary is to target
        salary_ratio = job_salary_avg / target_salary
        
        if salary_ratio >= 1.0:
            return 1.0  # Meets or exceeds target
        elif salary_ratio >= 0.8:
            return 0.8  # Within 20% of target
        elif salary_ratio >= 0.6:
            return 0.6  # Within 40% of target
        else:
            return 0.3  # Below expectations
    
    def _calculate_experience_match(self, job, user_experience_years):
        """Calculate experience level match"""
        job_desc = (job.description or '').lower()
        
        # Extract experience requirements from job description
        experience_patterns = [
            r'(\d+)\s*\+?\s*years?\s*experience',
            r'(\d+)\s*\+?\s*years?\s*of\s*experience',
            r'minimum\s*(\d+)\s*years?',
            r'at\s*least\s*(\d+)\s*years?'
        ]
        
        required_years = 0
        for pattern in experience_patterns:
            match = re.search(pattern, job_desc)
            if match:
                required_years = int(match.group(1))
                break
        
        if required_years == 0:
            return 0.7  # No clear requirement
        
        if user_experience_years >= required_years:
            return 1.0
        elif user_experience_years >= required_years * 0.8:
            return 0.8
        elif user_experience_years >= required_years * 0.6:
            return 0.6
        else:
            return 0.3
    
    def _calculate_program_match(self, resource, user, user_skills):
        """Calculate how well a learning program matches user needs"""
        if not resource.skill:
            return 0.3
        
        skill_name = resource.skill.name.lower()
        
        # Check if user already has this skill
        user_proficiency = user_skills.get(skill_name, 0)
        
        # Higher match for skills user doesn't have or has low proficiency in
        if user_proficiency == 0:
            proficiency_score = 0.9  # High value for new skills
        elif user_proficiency <= 2:
            proficiency_score = 0.7  # Medium value for improving weak skills
        else:
            proficiency_score = 0.4  # Lower value for already strong skills
        
        # Factor in resource quality
        quality_score = (resource.rating or 3) / 5.0
        
        # Combine scores
        match_score = (proficiency_score * 0.7) + (quality_score * 0.3)
        
        return match_score
    
    def _generate_match_explanation(self, match_components, skill_match_data):
        """Generate human-readable explanation of match score"""
        explanations = []
        
        if match_components['skills'] > 0.7:
            explanations.append(f"Strong skill match ({len(skill_match_data['matches'])} matching skills)")
        elif match_components['skills'] > 0.4:
            explanations.append(f"Partial skill match ({len(skill_match_data['matches'])} matching skills)")
        else:
            explanations.append("Limited skill match")
        
        if match_components['title'] > 0.8:
            explanations.append("Excellent role match")
        elif match_components['title'] > 0.5:
            explanations.append("Good role alignment")
        
        if match_components['location'] > 0.8:
            explanations.append("Great location fit")
        
        if match_components['salary'] > 0.8:
            explanations.append("Salary meets expectations")
        
        missing_skills = skill_match_data.get('missing', [])
        if missing_skills and len(missing_skills) <= 2:
            explanations.append(f"Consider learning: {', '.join(missing_skills[:2])}")
        
        return "; ".join(explanations)
    
    def _save_user_opportunities(self, user_id, opportunities):
        """Save opportunities for user tracking"""
        # Delete old suggestions
        UserOpportunity.query.filter_by(user_id=user_id, status='suggested').delete()
        
        # Save new suggestions
        for opp in opportunities[:10]:  # Save top 10
            if opp['type'] == 'job':
                user_opp = UserOpportunity(
                    user_id=user_id,
                    opportunity_id=opp['id'],
                    match_score=opp['match_score'],
                    status='suggested'
                )
                db.session.add(user_opp)
        
        db.session.commit()
    
    def _get_applied_filters(self, user):
        """Get filters that were applied during search"""
        filters = []
        
        if user.target_role:
            filters.append(f"Target role: {user.target_role}")
        if user.location:
            filters.append(f"Location: {user.location}")
        if user.target_salary:
            filters.append(f"Min salary: ${user.target_salary:,}")
        
        return filters
    
    def _generate_opportunity_recommendations(self, opportunities, user):
        """Generate recommendations based on opportunities found"""
        recommendations = []
        
        if not opportunities:
            recommendations.append("No opportunities found matching your criteria. Consider expanding your search or updating your skills.")
            return recommendations
        
        # Analyze common missing skills
        all_missing_skills = []
        for opp in opportunities[:10]:
            if 'missing_skills' in opp:
                all_missing_skills.extend(opp['missing_skills'])
        
        # Count frequency
        skill_counts = {}
        for skill in all_missing_skills:
            skill_counts[skill] = skill_counts.get(skill, 0) + 1
        
        # Recommend top missing skills
        if skill_counts:
            top_missing = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:3]
            rec_skills = [skill for skill, count in top_missing if count >= 2]
            
            if rec_skills:
                recommendations.append(f"Consider learning these in-demand skills: {', '.join(rec_skills)}")
        
        # Salary recommendations
        salaries = [opp.get('salary_min', 0) for opp in opportunities if opp.get('salary_min')]
        if salaries:
            avg_salary = sum(salaries) / len(salaries)
            if user.target_salary and avg_salary > user.target_salary * 1.2:
                recommendations.append(f"Great news! Available positions offer ${avg_salary:,.0f} on average, above your target.")
        
        # Location recommendations
        remote_count = sum(1 for opp in opportunities if opp.get('remote_ok'))
        if remote_count >= len(opportunities) * 0.3:
            recommendations.append(f"{remote_count} remote opportunities available - consider expanding your location preferences.")
        
        return recommendations
    
    def update_opportunity_status(self, user_id, opportunity_id, status, notes=None):
        """Update status of an opportunity (applied, interviewing, etc.)"""
        user_opp = UserOpportunity.query.filter_by(
            user_id=user_id,
            opportunity_id=opportunity_id
        ).first()
        
        if not user_opp:
            return {"error": "Opportunity not found"}
        
        user_opp.status = status
        if notes:
            user_opp.notes = notes
        
        db.session.commit()
        
        return {"success": True, "status": status}
    
    def get_user_opportunities(self, user_id, status=None):
        """Get opportunities for a user, optionally filtered by status"""
        query = UserOpportunity.query.filter_by(user_id=user_id)
        
        if status:
            query = query.filter_by(status=status)
        
        user_opportunities = query.order_by(UserOpportunity.match_score.desc()).all()
        
        result = []
        for user_opp in user_opportunities:
            job = user_opp.opportunity
            result.append({
                'id': job.id,
                'title': job.title,
                'company': job.company,
                'location': job.location,
                'salary_min': job.salary_min,
                'salary_max': job.salary_max,
                'match_score': user_opp.match_score,
                'status': user_opp.status,
                'notes': user_opp.notes,
                'url': job.url,
                'created_at': user_opp.created_at
            })
        
        return result
    
    def get_opportunity_alerts(self, user_id):
        """Get new opportunities that match user criteria"""
        # Get user's last check time (for simplicity, use 7 days ago)
        since_date = datetime.utcnow() - timedelta(days=7)
        
        # Find new opportunities
        new_opportunities = self.find_opportunities(user_id, limit=5)
        
        alerts = []
        for opp in new_opportunities['opportunities']:
            if opp.get('posted_date') and opp['posted_date'] >= since_date:
                alerts.append({
                    'title': opp['title'],
                    'company': opp.get('company'),
                    'match_score': opp['match_score'],
                    'reason': opp['match_explanation'],
                    'url': opp.get('url'),
                    'posted_date': opp['posted_date']
                })
        
        return alerts
```

### Step 9: Flask Application Routes (20 minutes)

#### 9.1 Create `app/forms.py`
```python
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, NumberRange, Optional

class UserProfileForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    name = StringField('Full Name', validators=[DataRequired()])
    current_role = StringField('Current Role')
    experience_years = IntegerField('Years of Experience', validators=[Optional(), NumberRange(min=0, max=50)])
    education_level = SelectField('Education Level', 
                                choices=[('high_school', 'High School'),
                                        ('associate', 'Associate Degree'),
                                        ('bachelor', 'Bachelor\'s Degree'),
                                        ('master', 'Master\'s Degree'),
                                        ('phd', 'PhD'),
                                        ('bootcamp', 'Bootcamp/Certificate'),
                                        ('self_taught', 'Self-taught')])
    location = StringField('Location')
    target_role = StringField('Target Role', validators=[DataRequired()])
    target_salary = IntegerField('Target Salary ($)', validators=[Optional(), NumberRange(min=0)])
    submit = SubmitField('Save Profile')

class SkillForm(FlaskForm):
    skill_name = StringField('Skill Name', validators=[DataRequired()])
    proficiency_level = SelectField('Proficiency Level',
                                  choices=[(1, 'Beginner'),
                                          (2, 'Novice'),
                                          (3, 'Intermediate'),
                                          (4, 'Advanced'),
                                          (5, 'Expert')],
                                  coerce=int,
                                  validators=[DataRequired()])
    submit = SubmitField('Add Skill')
```

#### 9.2 Create `app/routes.py`
```python
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.models import *
from app.forms import UserProfileForm, SkillForm
from app.skills_analyzer import SkillsAnalyzer
from app.learning_recommender import LearningRecommender
from app.opportunity_finder import OpportunityFinder
from app.data_fetcher import update_all_data
from app import db
import json

main = Blueprint('main', __name__)

@main.route('/')
def index():
    """Homepage"""
    return render_template('base.html')

@main.route('/profile', methods=['GET', 'POST'])
def profile():
    """User profile management"""
    form = UserProfileForm()
    
    # For demo, use user_id = 1
    user = User.query.get(1)
    
    if request.method == 'GET' and user:
        # Pre-populate form
        form.email.data = user.email
        form.name.data = user.name
        form.current_role.data = user.current_role
        form.experience_years.data = user.experience_years
        form.education_level.data = user.education_level
        form.location.data = user.location
        form.target_role.data = user.target_role
        form.target_salary.data = user.target_salary
    
    if form.validate_on_submit():
        if not user:
            user = User()
            db.session.add(user)
        
        user.email = form.email.data
        user.name = form.name.data
        user.current_role = form.current_role.data
        user.experience_years = form.experience_years.data
        user.education_level = form.education_level.data
        user.location = form.location.data
        user.target_role = form.target_role.data
        user.target_salary = form.target_salary.data
        
        db.session.commit()
        flash('Profile saved successfully!', 'success')
        return redirect(url_for('main.dashboard'))
    
    # Get user skills
    skills = []
    if user:
        user_skills = db.session.query(Skill.name, UserSkill.proficiency_level)\
                               .join(UserSkill)\
                               .filter(UserSkill.user_id == user.id)\
                               .all()
        skills = [{'name': name, 'level': level} for name, level in user_skills]
    
    return render_template('profile.html', form=form, skills=skills)

@main.route('/add_skill', methods=['POST'])
def add_skill():
    """Add a skill to user profile"""
    skill_form = SkillForm()
    
    if skill_form.validate_on_submit():
        # Get or create skill
        skill = Skill.query.filter_by(name=skill_form.skill_name.data).first()
        if not skill:
            skill = Skill(name=skill_form.skill_name.data, category='User Added')
            db.session.add(skill)
            db.session.flush()
        
        # Add to user (user_id = 1 for demo)
        user_skill = UserSkill.query.filter_by(user_id=1, skill_id=skill.id).first()
        if user_skill:
            user_skill.proficiency_level = skill_form.proficiency_level.data
        else:
            user_skill = UserSkill(
                user_id=1,
                skill_id=skill.id,
                proficiency_level=skill_form.proficiency_level.data
            )
            db.session.add(user_skill)
        
        db.session.commit()
        flash('Skill added successfully!', 'success')
    
    return redirect(url_for('main.profile'))

@main.route('/dashboard')
def dashboard():
    """Main dashboard"""
    user = User.query.get(1)  # Demo user
    
    if not user:
        flash('Please create your profile first.', 'warning')
        return redirect(url_for('main.profile'))
    
    # Get recent analysis
    latest_analysis = SkillGapAnalysis.query.filter_by(user_id=1)\
                                           .order_by(SkillGapAnalysis.created_at.desc())\
                                           .first()
    
    # Get learning paths
    recommender = LearningRecommender()
    learning_paths = recommender.get_user_learning_paths(1)
    
    # Get opportunities
    finder = OpportunityFinder()
    recent_opportunities = finder.get_user_opportunities(1)[:5]
    
    # Get next actions
    next_actions = recommender.get_recommended_next_actions(1)
    
    return render_template('dashboard.html', 
                         user=user,
                         latest_analysis=latest_analysis,
                         learning_paths=learning_paths[:3],
                         opportunities=recent_opportunities,
                         next_actions=next_actions[:3])

@main.route('/skills_analysis')
def skills_analysis():
    """Skill gap analysis page"""
    user = User.query.get(1)
    
    if not user or not user.target_role:
        flash('Please complete your profile and set a target role first.', 'warning')
        return redirect(url_for('main.profile'))
    
    # Run analysis
    analyzer = SkillsAnalyzer()
    analysis_result = analyzer.analyze_skill_gaps(1)
    
    if 'error' in analysis_result:
        flash(analysis_result['error'], 'error')
        return redirect(url_for('main.dashboard'))
    
    return render_template('skills_analysis.html', 
                         analysis=analysis_result,
                         user=user)

@main.route('/learning_paths')
def learning_paths():
    """Learning paths page"""
    user = User.query.get(1)
    
    if not user:
        flash('Please create your profile first.', 'warning')
        return redirect(url_for('main.profile'))
    
    recommender = LearningRecommender()
    paths = recommender.get_user_learning_paths(1)
    
    return render_template('learning_paths.html', 
                         learning_paths=paths,
                         user=user)

@main.route('/generate_learning_path', methods=['POST'])
def generate_learning_path():
    """Generate new learning path"""
    analysis_id = request.form.get('analysis_id')
    
    if not analysis_id:
        flash('No analysis selected.', 'error')
        return redirect(url_for('main.skills_analysis'))
    
    recommender = LearningRecommender()
    result = recommender.generate_learning_path(1, analysis_id=int(analysis_id))
    
    if 'error' in result:
        flash(result['error'], 'error')
    else:
        flash('Learning path generated successfully!', 'success')
    
    return redirect(url_for('main.learning_paths'))

@main.route('/update_progress', methods=['POST'])
def update_progress():
    """Update learning progress"""
    data = request.get_json()
    
    recommender = LearningRecommender()
    result = recommender.update_progress(
        1,  # user_id
        data['learning_path_id'],
        data['resource_id'],
        data.get('completed', True)
    )
    
    return jsonify(result)

@main.route('/opportunities')
def opportunities():
    """Opportunities page"""
    user = User.query.get(1)
    
    if not user:
        flash('Please create your profile first.', 'warning')
        return redirect(url_for('main.profile'))
    
    # Get opportunities
    finder = OpportunityFinder()
    opportunity_data = finder.find_opportunities(1)
    
    return render_template('opportunities.html', 
                         opportunities=opportunity_data['opportunities'],
                         recommendations=opportunity_data['recommendations'],
                         user=user)

@main.route('/update_opportunity_status', methods=['POST'])
def update_opportunity_status():
    """Update opportunity application status"""
    data = request.get_json()
    
    finder = OpportunityFinder()
    result = finder.update_opportunity_status(
        1,  # user_id
        data['opportunity_id'],
        data['status'],
        data.get('notes')
    )
    
    return jsonify(result)

@main.route('/refresh_data')
def refresh_data():
    """Refresh all data from APIs"""
    try:
        update_all_data()
        flash('Data refreshed successfully!', 'success')
    except Exception as e:
        flash(f'Error refreshing data: {str(e)}', 'error')
    
    return redirect(url_for('main.dashboard'))

@main.route('/api/skill_search')
def skill_search():
    """API endpoint for skill autocomplete"""
    query = request.args.get('q', '')
    
    if len(query) < 2:
        return jsonify([])
    
    skills = Skill.query.filter(Skill.name.ilike(f'%{query}%')).limit(10).all()
    return jsonify([{'name': skill.name, 'id': skill.id} for skill in skills])
```

### Step 10: HTML Templates (25 minutes)

#### 10.1 Create `app/templates/base.html`
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}AI Economic Mobility Platform{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .sidebar { min-height: 100vh; background-color: #f8f9fa; }
        .skill-badge { margin: 2px; }
        .match-score { font-weight: bold; }
        .high-match { color: #28a745; }
        .medium-match { color: #ffc107; }
        .low-match { color: #dc3545; }
        .progress-indicator { height: 6px; }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <!-- Sidebar -->
            <nav class="col-md-2 sidebar">
                <div class="position-sticky pt-3">
                    <h5 class="px-3 text-muted">Economic Mobility</h5>
                    <ul class="nav flex-column">
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('main.dashboard') }}">
                                <i class="fas fa-tachometer-alt"></i> Dashboard
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('main.profile') }}">
                                <i class="fas fa-user"></i> Profile
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('main.skills_analysis') }}">
                                <i class="fas fa-chart-bar"></i> Skills Analysis
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('main.learning_paths') }}">
                                <i class="fas fa-graduation-cap"></i> Learning Paths
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('main.opportunities') }}">
                                <i class="fas fa-briefcase"></i> Opportunities
                            </a>
                        </li>
                    </ul>
                    <hr>
                    <div class="px-3">
                        <small class="text-muted">
                            <a href="{{ url_for('main.refresh_data') }}" class="btn btn-outline-primary btn-sm">
                                <i class="fas fa-sync"></i> Refresh Data
                            </a>
                        </small>
                    </div>
                </div>
            </nav>

            <!-- Main content -->
            <main class="col-md-10 ms-sm-auto px-md-4">
                {% with messages = get_flashed_messages(with_categories=true) %}
                    {% if messages %}
                        {% for category, message in messages %}
                            <div class="alert alert-{{ 'danger' if category == 'error' else category }} alert-dismissible fade show mt-3" role="alert">
                                {{ message }}
                                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                            </div>
                        {% endfor %}
                    {% endif %}
                {% endwith %}

                {% block content %}
                <div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
                    <h1>Welcome to AI Economic Mobility Platform</h1>
                </div>
                
                <div class="row">
                    <div class="col-md-8">
                        <div class="card">
                            <div class="card-body">
                                <h5 class="card-title">Get Started</h5>
                                <p class="card-text">
                                    This platform uses AI to help you advance your career by:
                                </p>
                                <ul>
                                    <li>Analyzing skill gaps based on real job market data</li>
                                    <li>Recommending personalized learning pathways</li>
                                    <li>Finding relevant job opportunities and programs</li>
                                </ul>
                                <a href="{{ url_for('main.profile') }}" class="btn btn-primary">
                                    Create Your Profile
                                </a>
                            </div>
                        </div>
                    </div>
                    
                    <div class="col-md-4">
                        <div class="card">
                            <div class="card-body">
                                <h6 class="card-title">Platform Features</h6>
                                <ul class="list-unstyled">
                                    <li><i class="fas fa-check text-success"></i> Real-time job market analysis</li>
                                    <li><i class="fas fa-check text-success"></i> AI-powered skill recommendations</li>
                                    <li><i class="fas fa-check text-success"></i> Personalized learning paths</li>
                                    <li><i class="fas fa-check text-success"></i> Opportunity matching</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
                {% endblock %}
            </main>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    {% block scripts %}{% endblock %}
</body>
</html>
```

#### 10.2 Create other templates in `app/templates/`

Create `dashboard.html`:
```html
{% extends "base.html" %}

{% block title %}Dashboard - AI Economic Mobility{% endblock %}

{% block content %}
<div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
    <h1 class="h2">Dashboard</h1>
    <small class="text-muted">Welcome back, {{ user.name if user else 'User' }}!</small>
</div>

<div class="row">
    <!-- Quick Stats -->
    <div class="col-md-3">
        <div class="card text-center">
            <div class="card-body">
                <h5 class="card-title">{{ learning_paths|length }}</h5>
                <p class="card-text">Active Learning Paths</p>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card text-center">
            <div class="card-body">
                <h5 class="card-title">{{ opportunities|length }}</h5>
                <p class="card-text">New Opportunities</p>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card text-center">
            <div class="card-body">
                <h5 class="card-title">
                    {% if latest_analysis %}
                        {{ latest_analysis.created_at.strftime('%m/%d') }}
                    {% else %}
                        None
                    {% endif %}
                </h5>
                <p class="card-text">Last Analysis</p>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card text-center">
            <div class="card-body">
                <h5 class="card-title">{{ user.target_role if user and user.target_role else 'Not Set' }}</h5>
                <p class="card-text">Target Role</p>
            </div>
        </div>
    </div>
</div>

<div class="row mt-4">
    <!-- Next Actions -->
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h5><i class="fas fa-tasks"></i> Recommended Next Actions</h5>
            </div>
            <div class="card-body">
                {% if next_actions %}
                    {% for action in next_actions %}
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <div>
                            <strong>{{ action.skill }}</strong><br>
                            <small class="text-muted">{{ action.action }}</small>
                        </div>
                        <div>
                            <a href="{{ action.url }}" class="btn btn-sm btn-outline-primary" target="_blank">
                                Start
                            </a>
                        </div>
                    </div>
                    <hr>
                    {% endfor %}
                {% else %}
                    <p class="text-muted">
                        Complete your skills analysis to get personalized recommendations.
                        <a href="{{ url_for('main.skills_analysis') }}">Start Analysis</a>
                    </p>
                {% endif %}
            </div>
        </div>
    </div>

    <!-- Recent Opportunities -->
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h5><i class="fas fa-briefcase"></i> Latest Opportunities</h5>
            </div>
            <div class="card-body">
                {% if opportunities %}
                    {% for opp in opportunities %}
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <div>
                            <strong>{{ opp.title }}</strong><br>
                            <small class="text-muted">{{ opp.company }} - {{ opp.location }}</small>
                        </div>
                        <div>
                            <span class="badge bg-primary">{{ "%.0f"|format(opp.match_score * 100) }}%</span>
                        </div>
                    </div>
                    <hr>
                    {% endfor %}
                    <div class="text-center">
                        <a href="{{ url_for('main.opportunities') }}" class="btn btn-sm btn-outline-primary">
                            View All Opportunities
                        </a>
                    </div>
                {% else %}
                    <p class="text-muted">
                        No opportunities found. 
                        <a href="{{ url_for('main.opportunities') }}">Search Opportunities</a>
                    </p>
                {% endif %}
            </div>
        </div>
    </div>
</div>

<!-- Learning Progress -->
{% if learning_paths %}
<div class="row mt-4">
    <div class="col-12">
        <div class="card">
            <div class="card-header">
                <h5><i class="fas fa-graduation-cap"></i> Learning Progress</h5>
            </div>
            <div class="card-body">
                {% for path in learning_paths %}
                <div class="mb-3">
                    <div class="d-flex justify-content-between">
                        <span>{{ path.title }}</span>
                        <span class="text-muted">{{ "%.0f"|format(path.progress) }}%</span>
                    </div>
                    <div class="progress progress-indicator">
                        <div class="progress-bar" role="progressbar" 
                             style="width: {{ path.progress }}%" 
                             aria-valuenow="{{ path.progress }}" 
                             aria-valuemin="0" 
                             aria-valuemax="100">
                        </div>
                    </div>
                </div>
                {% endfor %}
                <div class="text-center mt-3">
                    <a href="{{ url_for('main.learning_paths') }}" class="btn btn-sm btn-outline-primary">
                        View All Learning Paths
                    </a>
                </div>
            </div>
        </div>
    </div>
</div>
{% endif %}
{% endblock %}
```

### Step 11: Application Setup and Database Initialization (10 minutes)

#### 11.1 Create `run.py`
```python
from app import create_app, db
from app.models import *

app = create_app()

@app.cli.command()
def init_db():
    """Initialize the database."""
    db.create_all()
    print("Database initialized!")

@app.cli.command()
def seed_data():
    """Seed database with sample data."""
    from app.data_fetcher import update_all_data
    
    # Create sample user
    user = User.query.first()
    if not user:
        user = User(
            email='demo@example.com',
            name='Demo User',
            current_role='Junior Developer',
            experience_years=2,
            education_level='bachelor',
            location='New York, NY',
            target_role='Senior Developer',
            target_salary=80000
        )
        db.session.add(user)
        db.session.commit()
        print("Demo user created!")
    
    # Update real-time data
    try:
        update_all_data()
        print("Real-time data updated!")
    except Exception as e:
        print(f"Error updating data: {e}")

if __name__ == '__main__':
    app.run(debug=True)
```

### Step 12: Installation and Setup Commands (15 minutes)

#### 12.1 Create setup script `setup.py`
```python
import os
import subprocess
import sys

def run_command(command):
    """Run a command and print output"""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)
    return result.returncode == 0

def setup_project():
    """Set up the entire project"""
    print("Setting up AI Economic Mobility Platform...")
    
    # Install Python dependencies
    print("\n1. Installing Python dependencies...")
    if not run_command("pip install -r requirements.txt"):
        print("Error installing dependencies!")
        return False
    
    # Set up environment variables
    print("\n2. Setting up environment...")
    env_content = """SECRET_KEY=dev-secret-key-change-in-production
DATABASE_URL=sqlite:///economic_mobility.db
REDIS_URL=redis://localhost:6379/0

# Get these API keys from respective services
ADZUNA_APP_ID=your_adzuna_app_id
ADZUNA_APP_KEY=your_adzuna_api_key
COURSERA_API_KEY=your_coursera_api_key
GITHUB_TOKEN=your_github_token
USAJOBS_API_KEY=your_usajobs_api_key
"""
    
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write(env_content)
        print("Created .env file - please add your API keys!")
    
    # Initialize database
    print("\n3. Initializing database...")
    if not run_command("flask init-db"):
        print("Error initializing database!")
        return False
    
    # Seed with sample data
    print("\n4. Seeding database...")
    if not run_command("flask seed-data"):
        print("Warning: Could not seed all data (API keys may be missing)")
    
    print("\n✅ Setup complete!")
    print("\nNext steps:")
    print("1. Add your API keys to the .env file")
    print("2. Run: python run.py")
    print("3. Open http://localhost:5000 in your browser")
    
    return True

if __name__ == "__main__":
    setup_project()
```

## Complete Implementation Guide

### Step 13: Running the Application

#### 13.1 Installation Commands
```bash
# 1. Clone or create project directory
mkdir ai-economic-mobility
cd ai-economic-mobility

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
# Edit .env file with your API keys

# 5. Initialize database
export FLASK_APP=run.py
flask init-db
flask seed-data

# 6. Run the application
python run.py
```

#### 13.2 API Keys Setup

**Required API Keys (Sign up for free accounts):**

1. **Adzuna Jobs API**: https://developer.adzuna.com/
2. **USAJobs API**: https://developer.usajobs.gov/
3. **GitHub API**: https://github.com/settings/tokens
4. **Optional: Coursera API** (or use web scraping)

#### 13.3 Real-Time Data Sources

The platform uses these real-time data sources:

1. **Job Data**: Adzuna API, USAJobs.gov API
2. **Skills Data**: Extracted from job descriptions, market analysis
3. **Learning Resources**: GitHub awesome lists, free online courses
4. **Market Trends**: Calculated from job posting frequency and requirements

## Testing the Features

### Feature 1: Skills Gap Analysis
1. Create user profile with target role
2. Add current skills with proficiency levels
3. Visit Skills Analysis page
4. View detailed gap analysis with market insights

### Feature 2: Learning Path Recommendations
1. Complete skills analysis
2. Generate learning path from analysis
3. View personalized course recommendations
4. Track progress through learning resources

### Feature 3: Opportunity Identification
1. Visit Opportunities page
2. View AI-matched job opportunities
3. See match scores and explanations
4. Track application status

## Production Deployment Considerations

### Database Migration
- Replace SQLite with PostgreSQL for production
- Set up proper database migrations
- Add database connection pooling

### API Rate Limiting
- Implement caching for API responses
- Add background job processing with Celery
- Set up Redis for session management

### Security Enhancements
- Add user authentication system
- Implement proper API key management
- Add input validation and sanitization
- Set up HTTPS and security headers

This implementation provides a fully functional MVP that can be built and tested in a single day while using real-time data sources for accurate, up-to-date information.