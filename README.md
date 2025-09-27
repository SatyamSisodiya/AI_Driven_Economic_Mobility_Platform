# AI-Driven Economic Mobility Platform

This platform helps users analyze their skill gaps, get personalized learning recommendations, and find relevant job opportunities using AI.

## Features

1. **Skill Gap Analysis**
   - Analyze current skills vs. target role requirements
   - Market demand insights
   - Prioritized skill development recommendations

2. **Learning Path Recommendations**
   - Personalized learning pathways
   - Progress tracking
   - Resource recommendations from multiple providers

3. **Opportunity Identification**
   - AI-powered job matching
   - Skill-based opportunity recommendations
   - Application tracking

## Setup Instructions

### Prerequisites

- Python 3.9 or higher
- pip (Python package installer)
- Redis (for Celery task queue)

### Installation Steps

1. Clone the repository:
```bash
git clone [repository-url]
cd AI_Driven_Economic_Mobility_Platform
```

2. Create and activate a virtual environment:
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Update the API keys in `.env` file:
     - Adzuna API: https://developer.adzuna.com/
     - USAJobs API: https://developer.usajobs.gov/
     - GitHub API: https://github.com/settings/tokens
     - (Optional) Coursera API

5. Initialize the database:
```bash
flask init-db
```

6. Seed initial data:
```bash
flask seed-data
```

7. Run the application:
```bash
python run.py
```

8. Access the application at http://localhost:5000

## Project Structure

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
├── config.py
├── run.py
├── requirements.txt
└── .env
```

## API Endpoints

### User Profile
- GET/POST `/profile` - Manage user profile
- POST `/add_skill` - Add a skill to user profile

### Analysis
- GET `/skills_analysis` - Get skill gap analysis
- GET `/learning_paths` - View learning paths
- POST `/generate_learning_path` - Generate new learning path

### Opportunities
- GET `/opportunities` - View job opportunities
- POST `/update_opportunity_status` - Update application status

### Data
- GET `/refresh_data` - Refresh all data from APIs
- GET `/api/skill_search` - Skill autocomplete API

## Development

### Adding New Features

1. Create new model in `app/models.py`
2. Add routes in `app/routes.py`
3. Create templates in `app/templates/`
4. Update database:
```bash
flask db migrate
flask db upgrade
```

### Testing

Run tests using:
```bash
python -m pytest tests/
```

## Production Deployment

For production deployment:

1. Use a production-grade database (PostgreSQL recommended)
2. Set up proper database migrations
3. Configure Celery for background tasks
4. Set up Redis for caching
5. Enable HTTPS
6. Implement user authentication
7. Set up proper logging
8. Configure rate limiting for APIs

## License

MIT License

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request
