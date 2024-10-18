
from flask import request, jsonify
from flask_restful import Resource
from models import Subject, db
from seclinkkenya.server.routes.auth import token_required   # type: ignore
from seclinkkenya.server.app import login_required

class Subject(Resource):
    @login_required
    @token_required
    def get(self, subject_id=None):
        if subject_id:
            subject = Subject.query.get_or_404(subject_id)
            return subject.to_dict(), 200
        subjects = Subject.query.all()
        return jsonify([subject.to_dict() for subject in subjects]), 200

    @login_required
    def post(self):
        data = request.get_json()
        subject = Subject(
            subject_name=data.get('subject_name'),
            subject_code=data.get('subject_code'),
            class_id=data.get('class_id'),
            teacher_id=data.get('teacher_id'),
        )
        db.session.add(subject)
        db.session.commit()
        return subject.to_dict(), 201

    @login_required
    def put(self, subject_id):
        data = request.get_json()
        subject = Subject.query.get_or_404(subject_id)
        subject.subject_name = data.get('subject_name')
        subject.subject_code = data.get('subject_code')
        db.session.commit()
        return subject.to_dict(), 200

    @login_required
    def delete(self, subject_id):
        subject = Subject.query.get_or_404(subject_id)
        db.session.delete(subject)
        db.session.commit()
        return '', 204
