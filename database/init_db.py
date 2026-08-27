import sys
import os

# Add root directory to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app import create_app
from backend.extensions import db
from backend.seed_data import seed_database

def init_database():
    """Initializes the database schema and seeds demo data."""
    print("[INFO] Initializing FlavorBridge database...")
    app = create_app()
    with app.app_context():
        # Ensure database directory exists
        db_path = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        if db_path.startswith('sqlite:///'):
            actual_file = db_path.replace('sqlite:///', '')
            dir_name = os.path.dirname(actual_file)
            if dir_name:
                os.makedirs(dir_name, exist_ok=True)
                
        db.create_all()
        print("[SUCCESS] Database tables created successfully.")
        seed_database()
        print("[SUCCESS] Database initialization completed successfully!")

if __name__ == '__main__':
    init_database()
