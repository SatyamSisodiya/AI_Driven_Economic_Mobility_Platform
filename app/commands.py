import click
from flask.cli import with_appcontext
from app import db
from app.models import User, Skill
from app.data_fetcher import update_all_data

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear existing data and create new tables."""
    db.drop_all()
    db.create_all()
    click.echo('Initialized the database.')

@click.command('populate-db')
@with_appcontext
def populate_db_command():
    """Populate database with initial data."""
    # Import seed data function
    from app.seed_data import seed_initial_data
    
    try:
        # Seed initial data
        seed_initial_data()
        click.echo('Database populated with initial data!')
    except Exception as e:
        click.echo(f'Error populating database: {str(e)}', err=True)
        raise
    # Create initial skills
    initial_skills = [
        ('Python', 'Programming Language'),
        ('JavaScript', 'Programming Language'),
        ('SQL', 'Database'),
        ('Machine Learning', 'AI/ML'),
        ('Data Analysis', 'Data Science'),
        ('Cloud Computing', 'Infrastructure'),
        ('DevOps', 'Infrastructure'),
        ('Web Development', 'Programming'),
        ('Agile', 'Methodology'),
        ('Communication', 'Soft Skills')
    ]
    
    for name, category in initial_skills:
        if not Skill.query.filter_by(name=name).first():
            skill = Skill(name=name, category=category)
            db.session.add(skill)
    
    # Create demo user
    if not User.query.filter_by(email='demo@example.com').first():
        demo_user = User(
            email='demo@example.com',
            name='Demo User',
            current_role='Junior Developer',
            experience_years=2,
            education_level='Bachelor\'s Degree',
            location='New York, NY',
            target_role='Senior Software Engineer',
            target_salary=120000
        )
        db.session.add(demo_user)
    
    db.session.commit()
    
    # Fetch and store job listings and learning resources
    update_all_data()
    
    click.echo('Database populated with initial data.')