from flask import request, session, jsonify, current_app as app
from flask_restful import Resource
import jwt
from seclinkkenya.server.models import Teacher, Parent, User, db
from routes.utils import login_required 
from flask_bcrypt import Bcrypt # type: ignore
import datetime

bcrypt = Bcrypt()

class Signup(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        role = data.get('role')

        if role == 'teacher':
            new_user = Teacher(username=username)
        elif role == 'parent':
            new_user = Parent(username=username)
        else:
            return jsonify({'message': 'Invalid role.'}), 400

        # Hash the password before storing
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user.password = hashed_password

        # Add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        return jsonify({'message': f'{role.capitalize()} registered successfully.'}), 201

class Login(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['role'] = user.role  # Store user role in session

            # Generate a JWT token for authentication
            token = jwt.encode(
                {"user_id": user.id, "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)},
                app.config['SECRET_KEY'],
                algorithm="HS256"
            )

            return jsonify({
                'id': user.id,
                'username': user.username,
                'role': user.role,
                'token': token
            }), 200
        
        return jsonify({'error': 'Invalid credentials'}), 401

class CheckSession(Resource):
    @login_required
    def get(self):
        user_id = session.get('user_id')
        user = User.query.get(user_id)
        if user:
            return {'id': user.id, 'username': user.username, 'role': user.role}, 200  # Include role in response
        return jsonify({'error': 'User not found'}), 404
    
class Logout(Resource):
    def delete(self):
        if session.get('user_id') is None:
            return jsonify({'error': 'Unauthorized'}), 401  # Return 401 when no active session
        session.pop('user_id', None)
        session.pop('role', None)  # Remove the role from session
        return {}, 204

