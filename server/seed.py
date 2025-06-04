#!/usr/bin/env python3
# seed.py

from app import app, db # Import app and db from your Flask app
from models import Plant # Import your Plant model
from decimal import Decimal # For handling Decimal type for price

# It's good practice to ensure the database is set up correctly
# within an app context, especially for standalone scripts like seed.py
with app.app_context():
    print("Seeding database...")

    # Clear existing data to prevent duplicates on re-seeding
    try:
        Plant.query.delete()
        db.session.commit()
        print("Existing plants deleted.")
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting existing plants (table might not exist yet): {e}")
        # If the table doesn't exist, it will raise an OperationalError here.
        # We'll proceed to create new plants, assuming migrations will create the table.

    # Create new plant instances as per user's provided seed.py
    # Note: Explicitly setting 'id' can cause issues with auto-incrementing primary keys
    # if the sequence is not reset. For testing, it might be fine, but for production,
    # it's generally better to let the database handle IDs.
    aloe = Plant(
        id=1,
        name="Aloe",
        image="./images/aloe.jpg", # Local image path, might need to be absolute for frontend
        price=Decimal('11.50'), # Ensure price is Decimal
    )

    zz_plant = Plant(
        id=2,
        name="ZZ Plant",
        image="./images/zz-plant.jpg", # Local image path, might need to be absolute for frontend
        price=Decimal('25.98'), # Ensure price is Decimal
    )

    # Add plants to the session
    db.session.add_all([aloe, zz_plant])

    # Commit the changes to the database
    try:
        db.session.commit()
        print("Plants seeded successfully!")
    except Exception as e:
        db.session.rollback()
        print(f"Error seeding plants: {e}")
