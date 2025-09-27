from app import db
from app.models import Skill, LearningResource, JobOpportunity
from datetime import datetime, timedelta
import json

def seed_initial_data():
    """Seed initial data for testing"""
    
    # Seed Skills
    skills_data = [
        {
            'name': 'Python',
            'category': 'Programming Language',
            'market_demand': 0.8,
            'avg_salary_impact': 85000
        },
        {
            'name': 'JavaScript',
            'category': 'Programming Language',
            'market_demand': 0.9,
            'avg_salary_impact': 80000
        },
        {
            'name': 'React',
            'category': 'Frontend Framework',
            'market_demand': 0.85,
            'avg_salary_impact': 90000
        },
        {
            'name': 'Node.js',
            'category': 'Backend Framework',
            'market_demand': 0.75,
            'avg_salary_impact': 88000
        },
        {
            'name': 'SQL',
            'category': 'Database',
            'market_demand': 0.8,
            'avg_salary_impact': 82000
        },
        {
            'name': 'AWS',
            'category': 'Cloud Platform',
            'market_demand': 0.85,
            'avg_salary_impact': 95000
        }
    ]

    # Add skills
    for skill_data in skills_data:
        if not Skill.query.filter_by(name=skill_data['name']).first():
            skill = Skill(**skill_data)
            db.session.add(skill)
    
    db.session.commit()

    # Seed Learning Resources
    resources_data = [
        {
            'title': 'Complete Python Bootcamp',
            'provider': 'Udemy',
            'url': 'https://www.udemy.com/complete-python-bootcamp',
            'skill_id': 1,  # Python
            'duration_hours': 40,
            'cost': 49.99,
            'rating': 4.7,
            'difficulty_level': 'beginner'
        },
        {
            'title': 'Modern JavaScript from the Beginning',
            'provider': 'Udemy',
            'url': 'https://www.udemy.com/modern-javascript',
            'skill_id': 2,  # JavaScript
            'duration_hours': 35,
            'cost': 49.99,
            'rating': 4.8,
            'difficulty_level': 'beginner'
        },
        {
            'title': 'React - The Complete Guide',
            'provider': 'Udemy',
            'url': 'https://www.udemy.com/react-the-complete-guide',
            'skill_id': 3,  # React
            'duration_hours': 45,
            'cost': 49.99,
            'rating': 4.9,
            'difficulty_level': 'intermediate'
        }
    ]

    # Add learning resources
    for resource_data in resources_data:
        if not LearningResource.query.filter_by(title=resource_data['title']).first():
            resource = LearningResource(**resource_data)
            db.session.add(resource)
    
    db.session.commit()

    # Seed Job Opportunities
    jobs_data = [
        {
            'title': 'Senior Python Developer',
            'company': 'Tech Corp',
            'location': 'New York, NY',
            'salary_min': 100000,
            'salary_max': 150000,
            'description': 'Looking for an experienced Python developer...',
            'requirements': json.dumps(['Python', 'SQL', 'AWS']),
            'url': 'https://example.com/jobs/1',
            'source': 'Internal',
            'posted_date': datetime.now() - timedelta(days=2),
            'expires_date': datetime.now() + timedelta(days=30),
            'remote_ok': True
        },
        {
            'title': 'Full Stack JavaScript Developer',
            'company': 'Web Solutions Inc',
            'location': 'San Francisco, CA',
            'salary_min': 90000,
            'salary_max': 140000,
            'description': 'Join our team as a Full Stack Developer...',
            'requirements': json.dumps(['JavaScript', 'React', 'Node.js']),
            'url': 'https://example.com/jobs/2',
            'source': 'Internal',
            'posted_date': datetime.now() - timedelta(days=1),
            'expires_date': datetime.now() + timedelta(days=30),
            'remote_ok': True
        }
    ]

    # Add job opportunities
    for job_data in jobs_data:
        if not JobOpportunity.query.filter_by(title=job_data['title'], company=job_data['company']).first():
            job = JobOpportunity(**job_data)
            db.session.add(job)
    
    db.session.commit()

if __name__ == '__main__':
    seed_initial_data()