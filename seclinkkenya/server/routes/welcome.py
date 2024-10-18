class Welcome(Resource):
    def get(self):
        return jsonify({"message": "Welcome to SecLink"})