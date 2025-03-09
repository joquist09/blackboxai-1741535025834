from app import app, db
from models.models import TennisCourt

def init_db():
    with app.app_context():
        # Create all database tables
        db.create_all()
        
        # Add sample tennis courts if they don't exist
        if TennisCourt.query.count() == 0:
            sample_courts = [
                TennisCourt(
                    name="Central Tennis Club",
                    address="123 Main St, City Center",
                    latitude=40.7128,
                    longitude=-74.0060,
                    available_hours='{"monday": "06:00-22:00", "tuesday": "06:00-22:00", "wednesday": "06:00-22:00", "thursday": "06:00-22:00", "friday": "06:00-22:00", "saturday": "08:00-20:00", "sunday": "08:00-20:00"}',
                    price_per_hour=30.00
                ),
                TennisCourt(
                    name="Riverside Courts",
                    address="456 River Road, Riverside",
                    latitude=40.7589,
                    longitude=-73.9851,
                    available_hours='{"monday": "07:00-21:00", "tuesday": "07:00-21:00", "wednesday": "07:00-21:00", "thursday": "07:00-21:00", "friday": "07:00-21:00", "saturday": "09:00-19:00", "sunday": "09:00-19:00"}',
                    price_per_hour=25.00
                ),
                TennisCourt(
                    name="Park View Tennis",
                    address="789 Park Ave, Green Park",
                    latitude=40.7829,
                    longitude=-73.9654,
                    available_hours='{"monday": "06:00-23:00", "tuesday": "06:00-23:00", "wednesday": "06:00-23:00", "thursday": "06:00-23:00", "friday": "06:00-23:00", "saturday": "07:00-22:00", "sunday": "07:00-22:00"}',
                    price_per_hour=35.00
                ),
                TennisCourt(
                    name="Community Tennis Center",
                    address="321 Community Blvd, Sports District",
                    latitude=40.7549,
                    longitude=-73.9840,
                    available_hours='{"monday": "08:00-20:00", "tuesday": "08:00-20:00", "wednesday": "08:00-20:00", "thursday": "08:00-20:00", "friday": "08:00-20:00", "saturday": "09:00-18:00", "sunday": "09:00-18:00"}',
                    price_per_hour=20.00
                )
            ]
            
            for court in sample_courts:
                db.session.add(court)
            
            db.session.commit()
            print("Sample tennis courts added successfully!")
        else:
            print("Database already contains tennis courts.")

if __name__ == '__main__':
    init_db()
