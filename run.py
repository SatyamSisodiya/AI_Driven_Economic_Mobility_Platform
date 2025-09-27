from app import create_app, db
from app.models import User
import os

app = create_app()

@app.cli.command()
def init_db():
    """Initialize the database."""
    with app.app_context():
        db.create_all()
        print("Database initialized!")

@app.cli.command()
def seed_data():
    """Seed database with sample data."""
    from app.data_fetcher import update_all_data
    
    with app.app_context():
        # Create sample user
        user = User.query.first()
        if not user:
            user = User(
                email="demo@example.com",
                name="Demo User",
                current_role="Software Developer",
                experience_years=3,
                education_level="bachelors",
                location="New York, NY",
                target_role="Senior Software Engineer",
                target_salary=120000
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