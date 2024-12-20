"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planets


app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)


@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    if "username" not in data or 'email' not in data:
        return jsonify({"error": "Invalid input, please set up username and password"}), 400
    existing_user = User.query.filter_by(username=data['username']).first()
    if (existing_user):
        return jsonify({"error": "username already exists."}), 409
    existing_email = User.query.filter_by(email=data['email']).first()
    if (existing_email):
        return jsonify({"error": "Email already exists."}), 409

    new_user = User(username=data['username'], email=data['email'], password=data['password'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"id": new_user.id, "username": new_user.username, "email": new_user.email}), 201
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    users = list(map(lambda x: x.serialize(), users))
    return jsonify(users)
@app.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    db.session.delete(user)
    db.session.commit()
    return jsonify({"User deleted succesfully"}), 200
@app.route('/people', methods=['GET'])
def get_people():
    people = People.query.all()
    people = list(map(lambda x: x.serialize(), people))
    return jsonify(people)
@app.route('/people/<int:id>', methods=['GET'])
def get_person(id):
    person = People.query.get(id)
    if not person:
        return jsonify({"error": "Person not found"}), 404
    return jsonify(person.serialize()), 200
@app.route('/people', methods=['POST'])
def create_person():
    data = request.get_json()
    if "name" not in data or "age" not in data or "country" not in data:
        return jsonify({"error": "Bad input"}), 400
    existing_name = People.query.filter_by(name=data['name']).first()
    if (existing_name):
        return jsonify({"error": "This person already exists."}), 409

    new_person = People(name=data['name'], age=data['age'], country=data['country'])
    db.session.add(new_person)
    db.session.commit()
    return jsonify({"id": new_person.id, "name": new_person.name, "age": new_person.age, "country": new_person.country, "message": "Person created succesfully"}), 201
@app.route('/people/<int:id>', methods=["DELETE"])
def delete_person(id):
    person = People.query.get(id)
    if not person:
        return jsonify({"Person not found"}), 404
    
    db.session.delete(person)
    db.session.commit()
    return jsonify({"message": "Person deleted succesfully"}), 200

@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planets.query.all()
    planets = list(map(lambda x: x.serialize(), planets))
    return jsonify(planets)

@app.route('/planets', methods=['POST'])
def create_planet():
    data = request.get_json()
    if "name" not in data or "population" not in data:
        return jsonify({"error": "Bad input"}), 400
    new_planet = Planets(name=data['name'], population=data['population'])
    db.session.add(new_planet)
    db.session.commit()
    return jsonify({"id": new_planet.id, "name": new_planet.name, "population": new_planet.population}), 201

@app.route('/users/favorites', methods=['GET'])
def get_favorites():
    


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
