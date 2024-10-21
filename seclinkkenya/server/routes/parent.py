# from flask import request, session, jsonify
# from seclinkkenya.server.models import Notifications, Parent, Student, db
# from flask_restful import Resource
# from seclinkkenya.server.routes.utils import token_required


# from flask import request, jsonify, session
# from flask_restful import Resource
# from routes.utils import token_required

# class Parent(Resource):
#     @token_required
#     def get(self, parent_id=None):
#         if parent_id:
#             # Fetch a specific parent
#             parent = Parent.query.get_or_404(parent_id)
#             return jsonify(parent.to_dict())
#         else:
#             # Fetch all parents (optional)
#             parents = Parent.query.all()
#             return jsonify([parent.to_dict() for parent in parents])

# class Notifications(Resource):
#     @token_required
#     def get(self):
#         parent_id = session.get('parent_id')
#         parent = Parent.query.get_or_404(parent_id)
#         notifications = Notifications.query.filter_by(parent_id=parent.id).all()
#         return jsonify([notification.to_dict() for notification in notifications]), 200

# class Student(Resource):
#     @token_required
#     def get(self):
#         parent_id = session.get('parent_id')
#         parent = Parent.query.get_or_404(parent_id)
#         students = Student.query.filter_by(parent_id=parent.id).all()
#         return jsonify([student.to_dict() for student in students]), 200
