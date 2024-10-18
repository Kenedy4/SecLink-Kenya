
from flask import jsonify, request
from flask_restful import Resource
from seclinkkenya.server.app import login_required
from models import Teacher, db
from seclinkkenya.server.routes.auth import token_required   # type: ignore

class Teacher(Resource):
    @login_required
    @token_required
    def get(self, teacher_id=None):
        if teacher_id:
            teacher = Teacher.query.get_or_404(teacher_id)
            return jsonify(teacher.to_dict()), 200
        teachers = Teacher.query.all()
        return jsonify([teacher.to_dict() for teacher in teachers]), 200

    @login_required
    @token_required
    def post(self):
        data = request.get_json()
        teacher = Teacher(
            name=data.get('name'),
            email=data.get('email'),
        )
        teacher.password = data.get('password')

        db.session.add(teacher)
        db.session.commit()
        return jsonify(teacher.to_dict()), 201

    @login_required
    @token_required
    def put(self, teacher_id):
        data = request.get_json()
        teacher = Teacher.query.get_or_404(teacher_id)
        teacher.name = data.get('name')
        teacher.email = data.get('email')
        db.session.commit()
        return jsonify(teacher.to_dict()), 200

    @login_required
    @token_required
    def delete(self, teacher_id):
        teacher = Teacher.query.get_or_404(teacher_id)
        db.session.delete(teacher)
        db.session.commit()
        return '', 204