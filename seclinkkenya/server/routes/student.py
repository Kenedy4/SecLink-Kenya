# from flask_restful import Resource
# from models import Student
# from flask import request, jsonify

# class Student (Resource):
#      def get(self, student_id=None):
#         if student_id:
#             # Get a single student by ID
#             student = Student.query.get(student_id)
#             if not student:
#                 return jsonify({'message': 'Student not found'}), 404
#             return jsonify(student.to_dict())  
#         else:
#             # Get all students
#             students = Student.query.all()
#             return jsonify([student.to_dict() for student in students])  
