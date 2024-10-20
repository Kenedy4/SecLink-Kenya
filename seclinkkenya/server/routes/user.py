from flask_restful import Resource
from flask import jsonify, request
from models import User, Parent, Teacher, db
from routes.utils import token_required

class User(Resource):
    @token_required
    def get(self, user_id=None):
        if user_id:
            # Fetch specific user by ID
            user = User.query.get(user_id)
            if not user:
                return jsonify({'error': 'User not found'}), 404
            return jsonify(user.to_dict()), 200
        else:
            # Fetch all users
            users = User.query.all()
            return jsonify([user.to_dict() for user in users]), 200

    @token_required
    def post(self):
        data = request.get_json()
        role = data.get('role')
        username = data.get('username')
        password = data.get('password')
        
        if role == 'teacher':
            new_user = Teacher(username=username)
        elif role == 'parent':
            new_user = Parent(username=username)
        else:
            return jsonify({'message': 'Invalid role.'}), 400

        # Hash the password before storing
        new_user.password = data.get('password')
        
        # Add the new user to the database
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({'message': f'{role.capitalize()} registered successfully.'}), 201

    @token_required
    def get(self, role):
        if role == 'parent':
            users = Parent.query.all()
        elif role == 'teacher':
            users = Teacher.query.all()
        else:
            return jsonify({'error': 'Invalid role provided'}), 400

        return jsonify([user.to_dict() for user in users]), 200

