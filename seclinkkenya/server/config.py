# import os
# from dotenv import load_dotenv

# # Load the environment variables from the .env file
# load_dotenv()

# class Config:
#     JWT_SECRET_KEY = os.getenv('SECRET_KEY')
#     SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///seclinkkenya.db')
#     SQLALCHEMY_TRACK_MODIFICATIONS = False
#     UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER')
#     ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}
#     PORT = int(os.getenv('PORT', 5555))
    
#     # Mail server settings
#     MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.googleemail.com')
#     MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
#     MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() in ['true', '1', 't']
#     MAIL_USERNAME = os.getenv('MAIL_USERNAME')
#     MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
