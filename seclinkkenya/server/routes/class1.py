from flask import jsonify
from flask_restful import Resource
from models import Class,  db
from routes.utils import token_required, login_required  # type: ignore


class Class(Resource):
    @token_required 
    @login_required
    def get(self, class_id=None):
        if class_id:
            # Fetch the class by class_id
            class_obj = Class.query.get(class_id)
            if not class_obj:
                return jsonify({'message': 'Class not found.'}), 404
            return jsonify(class_obj.to_dict()), 200
        else:
            # Fetch all classes if no class_id is provided
            classes = Class.query.all()
            return jsonify([class_obj.to_dict() for class_obj in classes]), 200
