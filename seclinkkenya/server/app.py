import os
from functools import wraps
from flask import Flask, jsonify, request, send_from_directory, session
from models import Grade, db, Student, Teacher, Parent, Class, Subject, Notifications, LearningMaterial, PasswordResetToken
from werkzeug.utils import secure_filename
from sqlalchemy import or_
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import datetime
import secrets
from flask_mail import Mail, Message
from flask_cors import CORS

# Flask app setup
app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'SECRET_KEY'  # Use a strong secret key in production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///seclinkkenya.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'docx', 'txt'}
app.config['PORT'] = 5555

# Flask-Mail setup
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'YOUR_EMAIL_ADDRESS'
app.config['MAIL_PASSWORD'] = 'YOUR_EMAIL_PASSWORD'

# Initializing necessary extensions
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)  # Using bcrypt for hashing
jwt = JWTManager(app)
mail = Mail(app)
CORS(app)

# Initializing the database
db.init_app(app)

# Ensure the 'uploads' folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Token required decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or not token.startswith("Bearer "):
            return jsonify({'message': 'Token is missing or in incorrect format!'}), 403

        try:
            token = token.split()[1]  # Extract token part
            decoded_token = jwt.decode_token(token)
            current_user = Teacher.query.get(decoded_token['identity']) or Parent.query.get(decoded_token['identity'])
            if not current_user:
                return jsonify({'message': 'User not found!'}), 404
        except Exception as e:
            return jsonify({'message': f'Error processing token: {str(e)}'}), 400

        # Pass current_user to the decorated function
        return f(current_user, *args, **kwargs)

    return decorated

# Verify password using bcrypt
def verify_password(user, entered_password):
    # Verify using bcrypt
    return bcrypt.check_password_hash(user.password, entered_password)

# Error handler for internal server errors
@app.errorhandler(500)
def internal_server_error(e):
    return jsonify({"error": "Internal server error", "message": str(e)}), 500

######  Routes ######

@app.route('/')
def welcome():
    return jsonify({"message": "Welcome to SecLink Kenya"}), 200

# Auth Routes

@app.route('/signup', methods=['POST'])
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    name = data.get('name')
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    subject = data.get('subject')
    role = data.get('role')

    # Check if the username already exists in Teacher or Parent tables
    existing_user = Teacher.query.filter_by(username=username).first() or Parent.query.filter_by(username=username).first()

    if existing_user:
        return {"message": "Username already exists"}, 400  # Return message if username exists

    # Proceed with user creation based on role
    if role == 'teacher':
        new_user = Teacher(name=name, username=username, subject=subject, email=email)
    elif role == 'parent':
        new_user = Parent(name=name, username=username, email=email)
    else:
        return {"message": 'Invalid role.'}, 400

    # Hash the password using bcrypt
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user.password = hashed_password  # Store the bcrypt-hashed password

    db.session.add(new_user)
    db.session.commit()

    return {"message": f'{role.capitalize()} registered successfully.'}, 201


@app.route('/login', methods=['POST'])
def login():
    # Parse the request data (username and password)
    data = request.get_json()

    # Ensure required fields are present
    if not data or not all(key in data for key in ['username', 'password']):
        return jsonify({"error": "Missing required fields"}), 400

    # Query both Teacher and Parent tables in one go using SQLAlchemy or_
    user = Teacher.query.filter(Teacher.username == data['username']).first() or \
           Parent.query.filter(Parent.username == data['username']).first()

    if user:
        print(f"User found: {user}")  # Debug the user found
        print(f"Stored Hashed Password: {user.password}")  # Debug the stored password hash
        print(f"Provided Password: {data['password']}")  # Debug the provided password
        
        # Verify the password using bcrypt's check_password_hash
        if bcrypt.check_password_hash(user.password, data['password']):
            # If password is valid, create and return JWT access token
            access_token = create_access_token(identity=user.id)
            return jsonify(access_token=access_token), 200
        else:
            # If password is incorrect
            print("Invalid password")  # Debug password mismatch
            return jsonify({"error": "Invalid credentials"}), 401

    # If user not found
    print("User not found")  # Debug user not found
    return jsonify({"error": "User not found"}), 404


@app.route('/check-session', methods=['GET'])
@jwt_required()  
def check_session():
    identity = get_jwt_identity()

    user = Teacher.query.filter_by(id=identity).first() or Parent.query.filter_by(id=identity).first()

    if not user:
        return jsonify({"error": 'User not found'}), 404

    return {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'role': 'teacher' if isinstance(user, Teacher) else 'parent'
    }, 200

@app.route('/logout', methods=['DELETE'])
def logout():
    session.pop('user_id', None)
    session.pop('role', None)
    return {}, 204

# Teacher Routes
@app.route('/teachers', methods=['GET'])
@token_required  # Only token_required is used
def get_teacher(current_user):
    students = Student.query.filter_by(teacher_id=current_user.id).all()
    parents = Parent.query.join(Student).filter(Student.teacher_id == current_user.id).all()

    return {
        'students': [student.to_dict() for student in students],
        'parents': [parent.to_dict() for parent in parents]
    }, 200

# Parent Routes
@app.route('/parents', methods=['GET'])
@token_required  # Only token_required is used
def get_parent(current_user):
    students = Student.query.filter_by(parent_id=current_user.id).all()
    notifications = Notifications.query.filter_by(parent_id=current_user.id).all()
    learning_materials = LearningMaterial.query.join(Student).filter(Student.parent_id == current_user.id).all()

    return {
        'students': [student.to_dict() for student in students],
        'notifications': [notification.to_dict() for notification in notifications],
        'learning_materials': [learning_material.to_dict() for learning_material in learning_materials]
    }, 200

# Notifications Routes
@app.route('/notifications', methods=['POST'])
@token_required  # Only token_required is used
def post_notification(current_user):
    data = request.get_json()
    notification = Notifications(
        message=data.get('message'),
        parent_id=data.get('parent_id')
    )
    db.session.add(notification)
    db.session.commit()
    return notification.to_dict(), 201

# Learning Material Routes
@app.route('/learning-materials', methods=['GET'])
@token_required
def get_learning_materials(current_user):
    learning_materials = LearningMaterial.query.all()
    return jsonify([lm.to_dict() for lm in learning_materials]), 200

@app.route('/upload', methods=['POST'])
@token_required
def upload_learning_material(current_user):
    if 'file' not in request.files:
        return {"error": "No file part"}, 400

    file = request.files['file']
    if file.filename == '':
        return {"error": "No selected file"}, 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        data = request.form
        learning_material = LearningMaterial(
            title=data.get('title'),
            file_path=file_path,
            teacher_id=current_user.id,
            subject_id=data.get('subject_id')
        )

        db.session.add(learning_material)
        db.session.commit()

        return {"message": "File uploaded successfully", "learning_material": learning_material.to_dict()}, 201
    else:
        return {"error": "Invalid file format"}, 400

@app.route('/download/<int:learning_material_id>', methods=['GET'])
@token_required
def download_learning_material(current_user, learning_material_id):
    learning_material = LearningMaterial.query.get_or_404(learning_material_id)
    file_path = learning_material.file_path
    file_name = os.path.basename(file_path)

    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], file_name, as_attachment=True)
    except FileNotFoundError:
        return {"error": "File not found"}, 404

# Password Reset Routes
@app.route('/password-reset-request', methods=['POST'])
def request_password_reset():
    data = request.get_json()
    email = data.get('email')

    user = Teacher.query.filter_by(email=email).first() or Parent.query.filter_by(email=email).first()

    if not user:
        return {"message": 'User not found'}, 404

    token = secrets.token_urlsafe(20)
    expiry = datetime.datetime.utcnow() + datetime.timedelta(hours=1)

    reset_token = PasswordResetToken(user_id=user.id, token=token, expiry_date=expiry)
    db.session.add(reset_token)
    db.session.commit()

    reset_link = f"{app.config['FRONTEND_URL']}/reset-password?token={token}"
    msg = Message('Password Reset Request', recipients=[email])
    msg.body = f"Use the following link to reset your password: {reset_link}"
    mail.send(msg)

    return {"message": 'Password reset link sent to your email.'}, 200

@app.route('/password-reset-confirm', methods=['POST'])
def confirm_password_reset():
    data = request.get_json()
    token = data.get('token')
    new_password = data.get('new_password')

    reset_token = PasswordResetToken.query.filter_by(token=token).first()

    if not reset_token:
        return {"message": 'Invalid or expired token'}, 400

    if reset_token.expiry_date < datetime.datetime.utcnow():
        return {"message": 'Token has expired'}, 400

    user = Teacher.query.get(reset_token.user_id) or Parent.query.get(reset_token.user_id)

    if not user:
        return {"message": 'User not found'}, 404

    user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')
    db.session.commit()

    db.session.delete(reset_token)
    db.session.commit()

    return {"message": 'Password has been updated successfully.'}, 200

@app.route('/contact', methods=['POST'])
def contact():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    message = data.get('message')

    # Send an email with the contact form data
    msg = Message(f"New Contact Form Submission from {name}", recipients=['your-email@example.com'])
    msg.body = f"Message from {name} ({email}):\n\n{message}"
    mail.send(msg)

    return jsonify({"message": "Message sent successfully!"}), 200


# App execution point
if __name__ == '__main__':
    app.run(port=5555, debug=True)
