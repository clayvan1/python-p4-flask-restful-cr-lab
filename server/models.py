from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import Column, Integer, String, Numeric # Import Numeric for Decimal type

# Initialize SQLAlchemy
db = SQLAlchemy()

# Define the Plant model
class Plant(db.Model, SerializerMixin):
    __tablename__ = 'plants' # Set the table name

    id = Column(Integer, primary_key=True) # Primary key
    name = Column(String, nullable=False) # Plant name, cannot be null
    image = Column(String, nullable=False) # Image URL, cannot be null
    price = Column(Numeric(10, 2), nullable=False) # Price as a Decimal, 10 total digits, 2 after decimal

    # Serialization rules to control JSON output
    # No specific rules needed for this simple model
    # serialize_rules = () 

    def __repr__(self):
        return f'<Plant {self.id}: {self.name} - ${self.price:.2f}>'

