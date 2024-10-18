class Class(Resource):
    @login_required
    def get(self, class_id=None):
        if class_id:
            class_obj = Class.query.get_or_404(class_id)
            return class_obj.to_dict(), 200
        classes = Class.query.all()
        return [class_obj.to_dict() for class_obj in classes], 200

    @login_required
    def post(self):
        data = request.get_json()
        class_obj = Class(
            class_name=data.get('class_name'),
            teacher_id=data.get('teacher_id'),
        )
        db.session.add(class_obj)
        db.session.commit()
        return class_obj.to_dict(), 201

    @login_required
    def put(self, class_id):
        data = request.get_json()
        class_obj = Class.query.get_or_404(class_id)
        class_obj.class_name = data.get('class_name')
        db.session.commit()
        return class_obj.to_dict(), 200

    @login_required
    def delete(self, class_id):
        class_obj = Class.query.get_or_404(class_id)
        db.session.delete(class_obj)
        db.session.commit()
        return '', 204