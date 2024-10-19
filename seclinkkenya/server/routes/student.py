from flask_restful import Resource
from models import Student, LearningMaterial
from flask import request, jsonify

class LearningMaterial(Resource):
    def get(self, student_id):
        student = Student.query.get(student_id)
        if not student:
            return {'message': 'Student not found'}, 404

        # Filter learning materials by subject IDs that the student is enrolled in
        learning_materials = LearningMaterial.query.filter(LearningMaterial.subject_id.in_(
            [subject.id for subject in student.subjects]
        )).all()

        return jsonify([material.serialize() for material in learning_materials])
