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
    
    # Register the database commands
    from app.commands import init_db_command, populate_db_command
    app.cli.add_command(init_db_command)
    app.cli.add_command(populate_db_command)
    
    return app