import os
from functools import wraps
from flask import Flask, jsonify, make_response, request, send_from_directory, session
from models import Class, LearningMaterial, Notifications, Student, Subject, db, Teacher, Parent, PasswordResetToken  # Import necessary models
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import random 
import string
import base64
import jwt
from sqlalchemy.exc import SQLAlchemyError
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_jwt_extended import  get_jwt, jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import secrets
from flask_mail import Mail, Message
from flask_cors import CORS
from config import Config  # Import the config class

# Flask app setup using Config class
app = Flask(__name__)
app.config.from_object(Config)  # Load configuration from config.py

# Initialize extensions

bcrypt = Bcrypt(app)
# jwt = JWTManager(app)
mail = Mail(app)
CORS(app)

# Initialize the database
db.init_app(app)
migrate = Migrate(app, db)
secret_key = base64.b64encode(os.urandom(24)).decode('utf-8')
# Helper function to check allowed file extensions
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'ppt', 'pptx'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Error handler for internal server errors
@app.errorhandler(500)
def internal_server_error(e):
    return jsonify({"error": "Internal server error", "message": str(e)}), 500


######  Routes ######

@app.route('/')
def welcome():
    return jsonify({"message": "Welcome to SecLink Kenya"}), 200

# Signup Endpoint
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()

    # Extract the fields from the request data
    name = data.get('name')
    username = data.get('username')
    password = data.get('password')  # Raw password from request
    email = data.get('email')
    subject = data.get('subject')  # Subject is only used if the user is a teacher
    role = data.get('role')  # Either 'Teacher' or 'Parent'

    # Check if all required fields are provided
    if not all([name, username, password, email, role]):
        return jsonify({'message': 'All fields are required'}), 400

    # Hash the password using bcrypt
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

    # Handle role-based registration
    if role.lower() == 'teacher':
        # Check if the subject is provided for the Teacher role
        if not subject:
            return jsonify({'message': 'Subject is required for Teacher role'}), 400
        
        # Create a new Teacher user
        new_user = Teacher(name=name, username=username, email=email, password=hashed_password, subject=subject)

    elif role.lower() == 'parent':
        # Create a new Parent user
        new_user = Parent(name=name, username=username, email=email, password=hashed_password)

    else:
        return jsonify({'message': 'Invalid role'}), 400

    # Add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    # Return success message
    return jsonify({'message': 'User registered successfully'}), 201


# Login Endpoint
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    # Ensure required fields are present
    username = data.get('username')
    password = data.get('password')

    if not all([username, password]):
        return jsonify({"message": "Missing required fields"}), 400

    # Query both Teacher and Parent tables for the user
    user = Teacher.query.filter_by(username=username).first() or \
        Parent.query.filter_by(username=username).first()
           
    if user and check_password_hash(user.password, password):   
        expiration_time = datetime.utcnow() + timedelta(hours=3)
        
        token = jwt.encode({'user_id': user.id, 'exp': expiration_time}, secret_key, algorithm='HS256')
        
        return jsonify({'token': token, 'message': 'Login Successful'}), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401  # If username or password is incorrect


# Token decoding helper function
def decode_token(token):
    try:
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return {'message': 'Token has expired'}, 401  # Token expired
    except jwt.InvalidTokenError:
        return {'message': 'Invalid token'}, 401  # Invalid token

@app.route('/logout', methods=['POST'])
@jwt_required()  # Ensure the user is logged in
def logout():
    # Here we can optionally blacklist the token or just return a success message
    jti = get_jwt()["jti"]  # JWT ID (jti) is unique identifier for the token
    
    
    return jsonify({"message": "Logged out successfully"}), 200

## Route to manage students ##
@app.route('/add-student', methods=['POST'])
def add_student():
    data = request.get_json()

    # Extract the fields from the request data
    name = data.get('name')
    dob = data.get('dob')  # Expected to be in string format
    overall_grade = data.get('overall_grade')
    class_id = data.get('class_id')
    teacher_id = data.get('teacher_id')
    parent_id = data.get('parent_id')

    # Check if all required fields are provided
    if not all([name, dob, overall_grade, class_id, teacher_id, parent_id]):
        return jsonify({'message': 'All fields are required'}), 400

    # Check if the class, teacher, and parent exist in the database
    try:
        student_class = Class.query.get(class_id)
        teacher = Teacher.query.get(teacher_id)
        parent = Parent.query.get(parent_id)
    except SQLAlchemyError as e:
        return jsonify({'message': 'Database lookup failed', 'error': str(e)}), 500

    if not student_class:
        return jsonify({'message': f'Class with id {class_id} not found'}), 404
    if not teacher:
        return jsonify({'message': f'Teacher with id {teacher_id} not found'}), 404
    if not parent:
        return jsonify({'message': f'Parent with id {parent_id} not found'}), 404

    # Create a new Student
    new_student = Student(
        name=name,
        dob=dob,  # dob remains in string format
        overall_grade=overall_grade,
        class_id=class_id,
        teacher_id=teacher_id,
        parent_id=parent_id,
        created_at=datetime.utcnow()  # Automatically set created_at
    )

    # Add the new student to the database with error handling
    try:
        db.session.add(new_student)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to add student', 'error': str(e)}), 500

    # Return success message
    return jsonify({'message': 'Student added successfully'}), 200

@app.route('/students/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def studend_by_id(id):
   student = Student.query.filter(Student.id == id).first()
  
   if student == None:
       return jsonify({"message": "Student not found."}), 404
   else:       
       if request.method == 'GET':
           student_dict = {
               "id": student.id,
               "name": student.name,
               "dob": student.dob,
               "class_id": student.class_id,
               "teacher_id": student.teacher_id,
               "parent_id": student.parent_id,
               "overall_grade": student.overall_grade
              
           }
           return jsonify(student_dict), 200
      
       elif request.method == 'PATCH':
           try:               
               data = request.get_json()
               name = data.get('name')
               dob = data.get('dob')
               class_id = data.get('class_id')
               teacher_id = data.get('teacher_id')
               parent_id = data.get('parent_id')
               overall_grade = data.get('overall_grade')
  
               if not name and not dob and not class_id and not teacher_id and not parent_id and not overall_grade:
                   return jsonify({"errors": "All fields are required."}), 400
  
               # Update the student data
               student.name = name
               student.dob = dob
               student.class_id = class_id
               student.teacher_id = teacher_id
               student.parent_id = parent_id
               student.overall_grade = overall_grade
              
               db.session.add(student)
               db.session.commit()
              
               # Response after successful student update
               updated_student_dict = {
                   "id": student.id,
                   "name": student.name,
                   "dob": student.dob,
                   "class_id":student.class_id,
                   "teacher_id": student.teacher_id,
                   "pranet_id": student.parent_id,
                   "overall_grade": student.overall_grade,
                   }
               return jsonify(updated_student_dict), 200
          
           # Handle validation errors
           except ValueError as ve:
               return jsonify({"errors": [str(ve)]}), 400
           
           # Fetch the student by its id
       elif request.method == 'DELETE':
            student = Student.query.filter_by(id=id).first()


            if not student:
                return make_response(jsonify({"errors": ["Student not found"]}), 404)


            try:
                # Delete the student
                db.session.delete(student)
                db.session.commit()
                return make_response(jsonify({"message": "Student deleted successfully"}), 200)


            except Exception as e:
                db.session.rollback() 
                return make_response(jsonify({"errors": [str(e)]}), 500)

@app.route('/students', methods=['GET'])
def get_students():
    students = Student.query.all()
    students_to_dict = [student.to_dict() for student in students]  # Convert each student to a dictionary
    return jsonify(students_to_dict), 200
 

##  Routes to Manage Learning Materials ##
@app.route('/learning-material', methods=['GET', 'POST', 'PUT', 'DELETE'])
@jwt_required()  # JWT-based authentication
def manage_learning_material():
    identity = get_jwt_identity()  # Get the user's identity from the JWT token

    if request.method == 'GET':
        # Handle retrieving learning materials (Parents only)
        if identity['role'] == 'Parent':
            materials = LearningMaterial.query.all()
            return jsonify([material.to_dict() for material in materials]), 200
        else:
            return jsonify({'message': 'Unauthorized'}), 403

    elif request.method == 'POST':
        # Handle file upload for new learning material (Teachers only)
        if identity['role'] != 'Teacher':
            return jsonify({"message": "Unauthorized access. Only teachers can upload materials."}), 403

        if 'file' not in request.files or not request.files['file']:
            return jsonify({'message': 'No file provided'}), 400

        file = request.files['file']

        # Validate file type using allowed_file function
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            # Save the file to the specified path
            try:
                file.save(file_path)
            except Exception as e:
                return jsonify({'message': f'File could not be saved: {str(e)}'}), 500

            # Create a new LearningMaterial entry in the database
            learning_material = LearningMaterial(
                title=request.form['title'],  # Title should be in form data
                file_path=file_path,
                teacher_id=identity['id'],  # Use the teacher ID from the JWT identity
                subject_id=request.form.get('subject_id')  # Assuming subject is provided
            )
            db.session.add(learning_material)
            db.session.commit()

            return jsonify({'message': 'Learning material uploaded successfully', 'file_path': file_path}), 200
        else:
            return jsonify({'message': 'Invalid file type'}), 400

    elif request.method == 'PUT':
        # Handle updating an existing learning material (Teachers only)
        if identity['role'] != 'Teacher':
            return jsonify({"message": "Unauthorized access. Only teachers can update materials."}), 403

        if 'id' not in request.form:
            return jsonify({'message': 'Material ID is required'}), 400

        # Find the material by ID
        learning_material = LearningMaterial.query.get(request.form['id'])
        if not learning_material:
            return jsonify({'message': 'Learning material not found'}), 404

        # Ensure the teacher updating the material is the one who uploaded it
        if learning_material.teacher_id != identity['id']:
            return jsonify({'message': 'Unauthorized. You can only update your own materials.'}), 403

        # Update the title if provided
        if 'title' in request.form:
            learning_material.title = request.form['title']

        # Handle file update if a file is provided
        if 'file' in request.files and allowed_file(request.files['file'].filename):
            file = request.files['file']
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            try:
                file.save(file_path)
                learning_material.file_path = file_path
            except Exception as e:
                return jsonify({'message': f'File could not be saved: {str(e)}'}), 500

        db.session.commit()
        return jsonify({'message': 'Learning material updated successfully'}), 200

    elif request.method == 'DELETE':
        # Handle deleting an existing learning material (Teachers only)
        if identity['role'] != 'Teacher':
            return jsonify({"message": "Unauthorized access. Only teachers can delete materials."}), 403

        material_id = request.form.get('id')  # Assuming 'id' is sent in the form data

        if not material_id:
            return jsonify({'message': 'Material ID is required'}), 400

        # Find the learning material by ID
        learning_material = LearningMaterial.query.get(material_id)
        if not learning_material:
            return jsonify({'message': 'Learning material not found'}), 404

        # Ensure the teacher deleting the material is the one who uploaded it
        if learning_material.teacher_id != identity['id']:
            return jsonify({'message': 'Unauthorized. You can only delete your own materials.'}), 403

        # Delete the file from the server
        try:
            os.remove(learning_material.file_path)  # Remove the file from the file system
        except Exception as e:
            return jsonify({'message': f'File could not be deleted: {str(e)}'}), 500

        # Delete the record from the database
        db.session.delete(learning_material)
        db.session.commit()

        return jsonify({'message': 'Learning material deleted successfully'}), 200

    return jsonify({'message': 'Invalid request method'}), 405  # Handle unsupported methods
@app.route('/download/<filename>', methods=['GET'])
@jwt_required()
def download_file(filename):
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404
    
# Route to Hanndle Notification ##
@app.route('/notifications', methods=['POST', 'GET'])
@jwt_required()
def manage_notifications():
    identity = get_jwt_identity()

    if request.method == 'POST':
        # Handle adding a notification (Teacher only)
        if identity['role'] == 'Teacher':
            data = request.get_json()
            notification = Notifications(
                message=data['message'],
                parent_id=data['parent_id']
            )
            db.session.add(notification)
            db.session.commit()

            return jsonify({'message': 'Notification sent'}), 200
        else:
            return jsonify({'message': 'Unauthorized'}), 403

    elif request.method == 'GET':
        # Handle getting notifications (Parent only)
        if identity['role'] == 'Parent':
            notifications = Notifications.query.filter_by(parent_id=identity['id']).all()
            return jsonify([notif.to_dict() for notif in notifications]), 200
        else:
            return jsonify({'message': 'Unauthorized'}), 403

    return jsonify({'message': 'Invalid request method'}), 405  # Handle unsupported methods

##  Route To Manage Classes ##

@app.route('/class', methods=['POST'])
def add_class():
    data = request.get_json()

    # Extract the fields from the request data
    class_name = data.get('class_name')
    teacher_id = data.get('teacher_id')

    # Check if all required fields are provided
    if not all([class_name, teacher_id]):
        return jsonify({'message': 'All fields are required'}), 400

    # Check if the teacher exists
    try:
        teacher = Teacher.query.get(teacher_id)
    except SQLAlchemyError as e:
        return jsonify({'message': 'Database lookup failed', 'error': str(e)}), 500

    if not teacher:
        return jsonify({'message': f'Teacher with id {teacher_id} not found'}), 404

    # Create a new Class
    new_class = Class(
        class_name=class_name,
        teacher_id=teacher_id,
    )

    #Add the new class to the database with error handling
    try:
        db.session.add(new_class)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to create a class', 'error': str(e)}), 500

    # #Return success message
    # return jsonify({'message': 'Class created successfully'}), 200
    # elif request.method == 'PUT':
    #     # Handle class update
    #     class_id = request.args.get('class_id')
    #     if not class_id:
    #         return jsonify({'message': 'Class ID is required for update'}), 400

    #     class_to_update = Class.query.get_or_404(class_id)

    #     # Ensure that the teacher who created the class or an Admin is updating
    #     if class_to_update.teacher_id != identity['id'] and identity['role'] != 'Admin':
    #         return jsonify({'message': 'Unauthorized to update this class'}), 403

    #     data = request.get_json()
    #     class_name = data.get('class_name')
    #     if class_name:
    #         class_to_update.class_name = class_name

    #     db.session.commit()
    #     return jsonify({'message': 'Class updated successfully', 'class': class_to_update.to_dict()}), 200

    # elif request.method == 'DELETE':
    #     # Handle class deletion
    #     class_id = request.args.get('class_id')
    #     if not class_id:
    #         return jsonify({'message': 'Class ID is required for deletion'}), 400

    #     class_to_delete = Class.query.get_or_404(class_id)

    #     # Ensure that the teacher who created the class or an Admin is deleting
    #     if class_to_delete.teacher_id != identity['id'] and identity['role'] != 'Admin':
    #         return jsonify({'message': 'Unauthorized to delete this class'}), 403

    #     db.session.delete(class_to_delete)
    #     db.session.commit()
    #     return jsonify({'message': 'Class deleted successfully'}), 200

    # return jsonify({'message': 'Invalid request method'}), 405  # Invalid HTTP method

@app.route('/classes', methods=['GET'])
@jwt_required()
def get_classes():
    identity = get_jwt_identity()

    # Allow teachers to view their own classes and admins to view all classes
    if identity['role'] == 'Teacher':
        classes = Class.query.filter_by(teacher_id=identity['id']).all()
        return jsonify([c.to_dict() for c in classes]), 200
    elif identity['role'] == 'Admin':
        classes = Class.query.all()
        return jsonify([class_.to_dict() for class_ in classes]), 200

    return jsonify({'message': 'Unauthorized'}), 403
@app.route('/subject', methods=['POST', 'PUT', 'DELETE'])
@jwt_required()
def manage_subject():
    identity = get_jwt_identity()

    if request.method == 'POST':
        # Handle creating a new subject (Teacher only)
        if identity['role'] == 'Teacher':
            data = request.get_json()
            subject_name = data.get('subject_name')
            subject_code = data.get('subject_code')
            class_id = data.get('class_id')

            if not (subject_name and subject_code and class_id):
                return jsonify({'message': 'Subject name, code, and class ID are required'}), 400

            new_subject = Subject(
                subject_name=subject_name,
                subject_code=subject_code,
                class_id=class_id,
                teacher_id=identity['id']
            )
            db.session.add(new_subject)
            db.session.commit()

            return jsonify({'message': 'Subject created successfully', 'subject': new_subject.to_dict()}), 201
        else:
            return jsonify({'message': 'Unauthorized'}), 403

    elif request.method == 'PUT':
        # Handle updating a subject (Teacher only)
        if identity['role'] == 'Teacher':
            data = request.get_json()
            subject_id = data.get('subject_id')  # Get subject ID from the request
            subject_to_update = Subject.query.get_or_404(subject_id)

            # Ensure that the teacher who created the subject is the one updating it
            if subject_to_update.teacher_id != identity['id']:
                return jsonify({'message': 'Unauthorized to update this subject'}), 403

            subject_name = data.get('subject_name')
            subject_code = data.get('subject_code')

            if subject_name:
                subject_to_update.subject_name = subject_name
            if subject_code:
                subject_to_update.subject_code = subject_code

            db.session.commit()
            return jsonify({'message': 'Subject updated successfully', 'subject': subject_to_update.to_dict()}), 200
        else:
            return jsonify({'message': 'Unauthorized'}), 403

    elif request.method == 'DELETE':
        # Handle deleting a subject (Teacher only)
        if identity['role'] == 'Teacher':
            subject_id = request.args.get('subject_id')  # Get subject ID from the query string
            subject_to_delete = Subject.query.get_or_404(subject_id)

            # Ensure that the teacher who created the subject is the one deleting it
            if subject_to_delete.teacher_id != identity['id']:
                return jsonify({'message': 'Unauthorized to delete this subject'}), 403

            db.session.delete(subject_to_delete)
            db.session.commit()
            return jsonify({'message': 'Subject deleted successfully'}), 200
        else:
            return jsonify({'message': 'Unauthorized'}), 403

    return jsonify({'message': 'Invalid request method'}), 405  # Handle unsupported methods

@app.route('/class/<int:class_id>/subjects', methods=['GET'])
@jwt_required()
def get_subjects_for_class(class_id):
    identity = get_jwt_identity()

    # Only the teacher who teaches the class can view the subjects for that class
    if identity['role'] == 'Teacher':  # Or any authorized role
        subjects = Subject.query.filter_by(class_id=class_id, teacher_id=identity['id']).all()
        return jsonify([subject.to_dict() for subject in subjects]), 200
    return jsonify({'message': 'Unauthorized'}), 403

if __name__ == '__main__':
     app.run(port=5555, debug=True)