import os
from flask import Flask
from flask_restful import Api
from models import db, User, Student, Teacher, Parent, Class, Subject, Notifications, LearningMaterial
from config import Config
from flask_mail import Mail
# from functools import wraps
from flask_migrate import Migrate # type: ignore
from flask_bcrypt import Bcrypt # type: ignore
from flask_jwt_extended import JWTManager # type: ignore
from flask_cors import CORS

# Importing routes
from routes.home import Welcome
from routes.parent import  Student,Parent
from routes.teacher import Teacher
from routes.student import LearningMaterial
from routes.class1 import Class
from routes.subject import Subject
# from routes.notification import Notifications
from routes.learningmaterial import LearningMaterial
from routes.learningmaterialupload import LearningMaterialUpload
from routes.learningmaterialdownload import LearningMaterialDownload
from routes.auth import CheckSession, Login, Logout, Signup
from routes.passwordreset import RequestPasswordReset, PasswordResetConfirm

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
mail = Mail(app)
CORS(app)
api = Api(app)

# Initialize the database
db.init_app(app)

# File upload configurations
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the 'uploads' folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Adding resources (endpoints)
api.add_resource(Welcome, '/', '/welcome')
api.add_resource(Signup, '/signup')
api.add_resource(Login, '/login')
api.add_resource(CheckSession, '/check-session')
api.add_resource(Logout, '/logout')

# Password reset endpoints
api.add_resource(RequestPasswordReset, '/password-reset-request') 
api.add_resource(PasswordResetConfirm, '/password-reset-confirm')


# Other resources
api.add_resource(Parent, '/parents', '/parents/<int:parent_id>')
api.add_resource(Student, '/students', '/students/<int:student_id>')
api.add_resource(Teacher, '/teachers', '/teachers/<int:teacher_id>')
api.add_resource(Class, '/classes', '/classes/<int:class_id>')
api.add_resource(Subject, '/subjects', '/subjects/<int:subject_id>')
# api.add_resource(Notification, '/notifications', '/notifications/<int:notification_id>')
api.add_resource(LearningMaterial, '/learning_materials', '/learning_materials/<int:learning_material_id>')
api.add_resource(LearningMaterialUpload, '/upload')
api.add_resource(LearningMaterialDownload, '/download/<int:learning_material_id>')

# app execution point
if __name__ == '__main__':
    app.run(port=Config.PORT, debug=True)
