import os
from flask import jsonify, send_from_directory, current_app as app
from flask_restful import Resource
from models import LearningMaterialDownload,  db
from auth import token_required   # type: ignore
from seclinkkenya.server.app import login_required


class LearningMaterialDownload(Resource):
    @login_required
    @token_required
    def get(self, learning_material_download_id):
        # Fetch the learning material by ID
        learning_material_download = LearningMaterialDownload.query.get_or_404(learning_material_download_id)

        # Extract the file path stored in the database
        file_path = learning_material_download.file_path
        file_name = os.path.basename(file_path)

        # Send the file to the user for download
        try:
            return send_from_directory(app.config['UPLOAD_FOLDER'], file_name, as_attachment=True)
        except FileNotFoundError:
            return jsonify({"error": "File not found"}), 404