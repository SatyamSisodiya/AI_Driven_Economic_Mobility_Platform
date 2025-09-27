import requests
import pandas as pd
from datetime import datetime, timedelta
from app.models import Skill, JobOpportunity, LearningResource
from app import db
from config import Config
import json
import time
from bs4 import BeautifulSoup

class DataFetcher:
    def __init__(self):
        self.config = Config()
    
    def fetch_job_market_data(self, location="United States", days_back=7):
        """Fetch real-time job data from multiple sources"""
        jobs = []
        
        try:
            # Adzuna API
            adzuna_url = f"https://api.adzuna.com/v1/api/jobs/{location}/search/1"
            params = {
                'app_id': self.config.ADZUNA_APP_ID,
                'app_key': self.config.ADZUNA_APP_KEY,
                'results_per_page': 50,
                'days_old': days_back,
                'what': 'software engineer developer'  # Default search term
            }
            
            response = requests.get(adzuna_url, params=params)
            if response.status_code == 200:
                data = response.json()
                for job in data.get('results', []):
                    jobs.append({
                        'title': job.get('title'),
                        'company': job.get('company', {}).get('display_name'),
                        'location': job.get('location', {}).get('display_name'),
                        'description': job.get('description'),
                        'salary_min': job.get('salary_min'),
                        'salary_max': job.get('salary_max'),
                        'url': job.get('redirect_url'),
                        'requirements': self._extract_requirements(job.get('description', '')),
                        'source': 'Adzuna',
                        'posted_date': datetime.strptime(job.get('created'), '%Y-%m-%dT%H:%M:%SZ'),
                        'remote_ok': 'remote' in job.get('description', '').lower()
                    })
        except Exception as e:
            print(f"Error fetching Adzuna data: {e}")
        
        # If no jobs found from Adzuna, use mock data
        if not jobs:
            jobs.extend(self._fetch_mock_jobs())
        
        return jobs
    
    def _fetch_mock_jobs(self):
        """Generate mock job data when API is not available"""
        jobs = []
        companies = [
            "Tech Innovations Ltd", "Digital Solutions Co", 
            "Future Systems Inc", "Data Dynamics", "AI Solutions Corp"
        ]
        
        locations = [
            "New York, NY", "San Francisco, CA", "Austin, TX", 
            "Boston, MA", "Seattle, WA"
        ]
        
        job_titles = [
            "Software Engineer", "Data Scientist", "Full Stack Developer",
            "Machine Learning Engineer", "DevOps Engineer", "Cloud Architect",
            "Frontend Developer", "Backend Engineer", "AI Specialist",
            "System Architect"
        ]
        
        for i in range(20):  # Generate 20 mock jobs
            base_salary = 70000 + (i * 5000)  # Vary salary by position
            title = job_titles[i % len(job_titles)]
            description = f"Exciting opportunity for a {title} to join our team. Requirements include:"
            
            jobs.append({
                'title': title,
                'company': companies[i % len(companies)],
                'location': locations[i % len(locations)],
                'description': description,
                'salary_min': base_salary,
                'salary_max': base_salary * 1.4,
                'url': f"https://example.com/jobs/{i}",
                'requirements': self._extract_requirements(description),
                'source': 'Mock Data',
                'posted_date': datetime.now() - timedelta(days=i % 7),
                'remote_ok': i % 3 == 0  # Every third job is remote
            })
        
        return jobs
    
    def _extract_requirements(self, description):
        """Extract skill requirements from job description using basic NLP"""
        common_skills = [
            'python', 'java', 'javascript', 'sql', 'html', 'css', 'react', 'node.js',
            'aws', 'azure', 'docker', 'kubernetes', 'agile', 'scrum', 'git', 'linux',
            'c++', 'c#', 'ruby', 'php', 'scala', 'swift', 'kotlin', 'rust',
            'mongodb', 'postgresql', 'mysql', 'redis', 'elasticsearch',
            'machine learning', 'ai', 'data science', 'blockchain', 'cloud',
            'devops', 'ci/cd', 'testing', 'security', 'networking'
        ]
        
        description_lower = description.lower()
        found_skills = [skill for skill in common_skills if skill in description_lower]
        return json.dumps(found_skills)
    
    def fetch_learning_resources(self):
        """Fetch learning resources from multiple sources"""
        resources = []
        
        # Coursera courses
        resources.extend(self._fetch_coursera_courses())
        
        # Free resources from GitHub
        resources.extend(self._fetch_github_learning_resources())
        
        # Add free learning resources
        resources.extend(self._get_free_learning_resources())
        
        return resources
    
    def _fetch_coursera_courses(self):
        """Fetch popular Coursera courses"""
        popular_courses = []
        
        try:
            # Since Coursera API access is limited, we'll scrape their website
            url = "https://www.coursera.org/browse/computer-science"
            response = requests.get(url)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                courses = soup.find_all('div', class_='card-info')
                
                for course in courses:
                    title = course.find('h2')
                    if title:
                        title = title.text.strip()
                        
                        # Try to match the course with a skill
                        skill = None
                        for s in Skill.query.all():
                            if s.name.lower() in title.lower():
                                skill = s
                                break
                        
                        popular_courses.append({
                            'title': title,
                            'provider': 'Coursera',
                            'url': 'https://www.coursera.org' + course.find('a')['href'] if course.find('a') else None,
                            'skill_id': skill.id if skill else None,
                            'duration_hours': 40,  # Average course duration
                            'cost': 49.99,  # Average course cost
                            'rating': 4.5,  # Default rating
                            'difficulty_level': 'intermediate'  # Default level
                        })
        except Exception as e:
            print(f"Error fetching Coursera data: {e}")
        
        return popular_courses
    
    def _fetch_github_learning_resources(self):
        """Fetch learning resources from GitHub"""
        resources = []
        
        try:
            headers = {'Authorization': f'token {self.config.GITHUB_TOKEN}'}
            
            # Search for educational repositories
            search_terms = ['learning-path', 'tutorial', 'course', 'learning']
            for term in search_terms:
                url = f"https://api.github.com/search/repositories?q={term}+in:name,description+stars:>100&sort=stars"
                response = requests.get(url, headers=headers)
                
                if response.status_code == 200:
                    repos = response.json().get('items', [])
                    for repo in repos[:10]:  # Top 10 results per term
                        # Determine the skill category
                        skill_category = self._infer_skill_from_name(repo['name'])
                        
                        # Find or create skill
                        skill = Skill.query.filter_by(name=skill_category).first()
                        if not skill:
                            skill = Skill(name=skill_category)
                            db.session.add(skill)
                            db.session.flush()
                        
                        resources.append({
                            'title': repo['name'],
                            'provider': 'GitHub',
                            'url': repo['html_url'],
                            'skill_id': skill.id,
                            'duration_hours': 20,  # Estimated time
                            'cost': 0,  # Free
                            'rating': repo['stargazers_count'] / 1000,  # Convert stars to rating
                            'difficulty_level': 'intermediate'  # Default level
                        })
                
                time.sleep(1)  # Respect rate limiting
        except Exception as e:
            print(f"Error fetching GitHub data: {e}")
        
        return resources
    
    def _get_free_learning_resources(self):
        """Get curated list of free learning resources"""
        return [
            {
                'title': 'freeCodeCamp',
                'provider': 'freeCodeCamp',
                'url': 'https://www.freecodecamp.org',
                'duration_hours': 300,
                'cost': 0,
                'rating': 4.8,
                'difficulty_level': 'beginner'
            },
            {
                'title': 'The Odin Project',
                'provider': 'The Odin Project',
                'url': 'https://www.theodinproject.com',
                'duration_hours': 200,
                'cost': 0,
                'rating': 4.7,
                'difficulty_level': 'beginner'
            },
            {
                'title': 'MIT OpenCourseWare',
                'provider': 'MIT',
                'url': 'https://ocw.mit.edu/courses/computer-science/',
                'duration_hours': 400,
                'cost': 0,
                'rating': 4.9,
                'difficulty_level': 'advanced'
            }
        ]
    
    def _infer_skill_from_name(self, name):
        """Infer skill category from repository name"""
        name_lower = name.lower()
        
        if 'python' in name_lower:
            return 'Python'
        elif 'javascript' in name_lower or 'js' in name_lower:
            return 'JavaScript'
        elif 'java' in name_lower:
            return 'Java'
        elif 'react' in name_lower:
            return 'React'
        elif 'node' in name_lower:
            return 'Node.js'
        elif 'angular' in name_lower:
            return 'Angular'
        elif 'vue' in name_lower:
            return 'Vue.js'
        elif 'machine-learning' in name_lower or 'ml' in name_lower:
            return 'Machine Learning'
        elif 'data-science' in name_lower or 'datascience' in name_lower:
            return 'Data Science'
        elif 'aws' in name_lower:
            return 'AWS'
        elif 'docker' in name_lower:
            return 'Docker'
        elif 'kubernetes' in name_lower or 'k8s' in name_lower:
            return 'Kubernetes'
        
        return 'General Programming'
    
    def update_skill_market_demand(self):
        """Update skill market demand based on job postings"""
        # Get all job postings from last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        jobs = JobOpportunity.query.filter(JobOpportunity.posted_date >= thirty_days_ago).all()
        
        skill_counts = {}
        total_jobs = len(jobs)
        
        for job in jobs:
            if job.requirements:
                skills = json.loads(job.requirements)
                for skill in skills:
                    if skill in skill_counts:
                        skill_counts[skill]['count'] += 1
                        if job.salary_max:
                            skill_counts[skill]['salaries'].append(job.salary_max)
                    else:
                        skill_counts[skill] = {
                            'count': 1,
                            'salaries': [job.salary_max] if job.salary_max else []
                        }
        
        # Update skill market demand and salary impact in database
        for skill_name, data in skill_counts.items():
            skill = Skill.query.filter(Skill.name.ilike(skill_name)).first()
            if skill:
                skill.market_demand = data['count'] / total_jobs
                if data['salaries']:
                    skill.avg_salary_impact = sum(data['salaries']) / len(data['salaries'])
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
            company=job_data['company'],
            location=job_data['location']
        ).first()
        
        if not existing_job:
            job = JobOpportunity(**job_data)
            db.session.add(job)
    
    # Update learning resources
    resources = fetcher.fetch_learning_resources()
    for resource_data in resources:
        # Check if resource already exists
        existing_resource = LearningResource.query.filter_by(
            title=resource_data['title'],
            provider=resource_data['provider']
        ).first()
        
        if not existing_resource:
            resource = LearningResource(**resource_data)
            db.session.add(resource)
    
    # Update skill market demand
    fetcher.update_skill_market_demand()
    
    db.session.commit()
    print("Data update completed successfully!")