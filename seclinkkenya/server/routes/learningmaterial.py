from flask import jsonify
from flask_restful import Resource
from models import LearningMaterial, db
from seclinkkenya.server.routes.auth import token_required   # type: ignore
from seclinkkenya.server.app import login_required


class LearningMaterial(Resource):
    @login_required
    @token_required
    def get(self, learning_material_id=None):
        if learning_material_id:
            learning_material = LearningMaterial.query.get_or_404(learning_material_id)
            return learning_material.to_dict(), 200
        learning_materials = LearningMaterial.query.all()
        return jsonify([learning_material.to_dict() for learning_material in learning_materials]), 200

    @login_required
    def delete(self, learning_material_id):
        learning_material = LearningMaterial.query.get_or_404(learning_material_id)
        db.session.delete(learning_material)
        db.session.commit()
        return '', 204