from flask import request, session, jsonify
from flask_restful import Resource
from models import Parent, Notification, Student
from seclinkkenya.server.routes.auth import token_required   # type: ignore
from functools import wraps

# Helper function to check if a parent is logged in
def parent_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'parent_id' not in session:
            return jsonify({"error": "Unauthorized access, please log in as a parent"}), 401
        return f(*args, **kwargs)
    return decorated_function

class Notifications(Resource):
    @token_required
    def get(self):
        parent_id = session.get('parent_id')
        parent = Parent.query.get_or_404(parent_id)
        notifications = Notification.query.filter_by(parent_id=parent.id).all()
        return jsonify([notification.to_dict() for notification in notifications]), 200

class Student(Resource):
    @parent_login_required
    def get(self):
        parent_id = session.get('parent_id')
        parent = Parent.query.get_or_404(parent_id)
        students = Student.query.filter_by(parent_id=parent.id).all()
        return jsonify([student.to_dict() for student in students]), 200
