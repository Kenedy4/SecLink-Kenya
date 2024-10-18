class LearningMaterialDownload(Resource):
    @login_required
    def get(self, learning_material_id):
        # Fetch the learning material by ID
        learning_material = LearningMaterial.query.get_or_404(learning_material_id)

        # Extract the file path stored in the database
        file_path = learning_material.file_path
        file_name = os.path.basename(file_path)

        # Send the file to the user for download
        try:
            return send_from_directory(app.config['UPLOAD_FOLDER'], file_name, as_attachment=True)
        except FileNotFoundError:
            return {"error": "File not found"}, 404