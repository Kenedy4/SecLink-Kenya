class LearningMaterialUpload(Resource):
    @login_required
    def post(self):
        # Ensure the user is a teacher
        user_id = session.get('user_id')
        teacher = Teacher.query.get(user_id)

        if 'file' not in request.files:
            return {"error": "No file part"}, 400

        file = request.files['file']

        if file.filename == '':
            return {"error": "No selected file"}, 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # Save the file path and related information in the database
            data = request.form  # Get additional form data
            learning_material = LearningMaterial(
                title=data.get('title'),
                file_path=filename,
                teacher_id=teacher.id,
                subject_id=data.get('subject_id')  # Assuming subject is provided
            )

            db.session.add(learning_material)
            db.session.commit()

            return {"message": "File uploaded successfully"}, 201

        return {"error": "Invalid file format"}, 400