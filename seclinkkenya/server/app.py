import os
from flask import Flask, session, jsonify # type: ignore
# from flask_sqlalchemy import SQLAlchemy # type: ignore
from flask_restful import Api, Resource # type: ignore
from seclinkkenya.server.routes.home import Welcome
from seclinkkenya.server.routes.parent import Parent
from seclinkkenya.server.routes.teacher import Teacher
from seclinkkenya.server.routes.class1 import Class
from seclinkkenya.server.routes.subject import Subject
from seclinkkenya.server.routes.notification import Notification
from seclinkkenya.server.routes.learningmaterial import LearningMaterial
from seclinkkenya.server.routes.learningmaterialupload import LearningMaterialUpload
from seclinkkenya.server.routes.learningmaterialdownload import LearningMaterialDownload
from seclinkkenya.server.routes.auth import CheckSession, Login, Logout, Signup
from seclinkkenya.server.routes.PasswordResetRequest import PasswordResetRequest, PasswordResetConfirm
from models import db, Student, Teacher, Class, Subject, Notification, LearningMaterial
from config import Config
# from werkzeug.utils import secure_filename # type: ignore
from functools import wraps
from flask_migrate import Migrate #type: ignore
from seclinkkenya.server.routes.auth import CheckSession, Login, Logout, Signup
from sqlalchemy.exc import IntegrityError # type: ignore
from flask_bcrypt import Bcrypt # type: ignore
from flask_jwt import Jwt # type: ignore
# from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
app.config.from_object(Config)

migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
CORS(app)
api = Api(app)

# Initialize extensions
# db = SQLAlchemy()
db.init_app(app)
# Directory for saving uploaded files
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Directory for saving uploaded files
app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER

# Ensure the 'uploads' folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Helper function to check if a user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"error": "Unauthorized access, please log in"}), 401
        return f(*args, **kwargs)
    return decorated_function

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf', 'docx', 'txt'}

api.add_resource(Welcome, '/', '/welcome')
api.add_resource(Signup, '/signup')
api.add_resource(Login, '/login')
api.add_resource(CheckSession, '/check-session')
api.add_resource(Logout, '/logout')
api.add_resource(PasswordResetRequest, '/password-reset-request')
api.add_resource(PasswordResetConfirm, '/password-reset-confirm')

api.add_resource(Parent, '/parents', '/parents/<int:parent_id>')
api.add_resource(Teacher, '/teachers', '/teachers/<int:teacher_id>')
api.add_resource(Class, '/classes', '/classes/<int:class_id>')
api.add_resource(Subject, '/subjects', '/subjects/<int:subject_id>')
api.add_resource(Notification, '/notifications', '/notifications/<int:notification_id>')
api.add_resource(LearningMaterial, '/learning_materials', '/learning_materials/<int:learning_material_id>')
api.add_resource(LearningMaterialUpload, '/upload')
api.add_resource(LearningMaterialDownload, '/download/<int:learning_material_id>')

if __name__ == '__main__':
    app.run(port=Config.PORT, debug=True) 