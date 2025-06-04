from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate
from flask_cors import CORS # Import CORS
from sqlalchemy.exc import IntegrityError # Import IntegrityError for database errors
from datetime import datetime # Import datetime for timestamps
from decimal import Decimal # Import Decimal for price column

# Assuming models.py will define the Plant model
from models import db, Plant 

app = Flask(__name__)
# Configure the database URI to place app.db directly in the 'server' directory.
# This simplifies the path and avoids potential nested 'instance' issues.
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False # Ensure JSON output is not compacted for readability

# Initialize CORS for the Flask app
CORS(app)

migrate = Migrate(app, db)

db.init_app(app) # Initialize db with the app

# --- Custom Error Handlers ---
@app.errorhandler(404)
def not_found(error):
    # Ensure the error message is a string for jsonify
    message = str(error) if isinstance(error, Exception) else "Resource not found"
    return make_response(jsonify({"error": message}), 404)

@app.errorhandler(400)
def bad_request(error):
    # Ensure the error message is a string for jsonify
    message = str(error) if isinstance(error, Exception) else "Bad Request"
    return make_response(jsonify({"error": message}), 400)

@app.errorhandler(500)
def internal_server_error(error):
    # Ensure the error message is a string for jsonify
    message = str(error) if isinstance(error, Exception) else "Internal Server Error"
    return make_response(jsonify({"error": message}), 500)

# --- API Routes ---

@app.route('/')
def home():
    return '<h1>Plant Store API</h1>' # Updated home route message

# GET /plants: returns an array of all plants as JSON.
@app.route('/plants', methods=['GET'])
def get_plants():
    try:
        # Query all plants
        plants = Plant.query.all()
        # Serialize each plant object to a dictionary
        plants_data = [plant.to_dict() for plant in plants]
        return make_response(jsonify(plants_data), 200)
    except Exception as e:
        # Catch any exceptions during database query or serialization
        db.session.rollback() # Rollback in case of error
        return internal_server_error(str(e))

# GET /plants/:id: returns a single plant as JSON.
@app.route('/plants/<int:id>', methods=['GET'])
def get_plant_by_id(id):
    plant = Plant.query.get(id) # Get plant by ID

    # If plant not found, return 404
    if not plant:
        return not_found(f"Plant with id {id} not found")

    try:
        plant_data = plant.to_dict()
        return make_response(jsonify(plant_data), 200)
    except Exception as e:
        return internal_server_error(str(e))

# POST /plants: creates a new plant and returns the newly created plant as JSON.
@app.route('/plants', methods=['POST'])
def create_plant():
    data = request.get_json() # Get JSON data from the request body

    # Validate required fields: name, image, price
    if not data or not all(k in data for k in ('name', 'image', 'price')):
        return bad_request("Missing required fields: 'name', 'image', and 'price'")

    name = data.get('name')
    image = data.get('image')
    price_str = data.get('price') # Get price as string initially

    # Basic validation for empty strings
    if not name or not image or price_str is None: # Check for None explicitly for price
        return bad_request("Name, image, and price cannot be empty.")

    try:
        # Convert price to Decimal
        price = Decimal(str(price_str)) # Convert to string first to handle float/int input
    except (ValueError, TypeError):
        return bad_request("Price must be a valid number.")

    try:
        # Create a new Plant instance
        new_plant = Plant(name=name, image=image, price=price)
        db.session.add(new_plant) # Add to session
        db.session.commit() # Commit to database

        # Return new plant with 201 Created status
        return make_response(jsonify(new_plant.to_dict()), 201)
    except IntegrityError:
        db.session.rollback()
        # This error typically occurs if there's a unique constraint violation (not expected for this model)
        return bad_request("Failed to create plant due to data integrity issue.")
    except Exception as e:
        db.session.rollback() # Rollback in case of other errors
        return internal_server_error(str(e))


# DELETE /plants/<int:id>: deletes the plant from the database and returns a JSON message.
# This route was not explicitly requested in the latest prompt but is a common CRUD operation.
# Keeping it for completeness if the frontend expects it.
@app.route('/plants/<int:id>', methods=['DELETE'])
def delete_plant(id):
    plant = Plant.query.get(id) # Get plant by ID

    # If plant not found, return 404
    if not plant:
        return not_found(f"Plant with id {id} not found")

    try:
        db.session.delete(plant) # Delete from session
        db.session.commit() # Commit to database

        # Return success message with 200 OK status
        return make_response(jsonify({"message": f"Plant with id {id} successfully deleted"}), 200)
    except Exception as e:
        db.session.rollback() # Rollback in case of error
        return internal_server_error(str(e))

if __name__ == '__main__':
    # Add an app context to ensure db.create_all() works outside of a request
    with app.app_context():
        # This line creates tables if they don't exist. While migrations are preferred
        # for schema management, this can be useful for initial setup or testing
        # if migrations are temporarily skipped.
        db.create_all() 
    app.run(port=5555, debug=True)
