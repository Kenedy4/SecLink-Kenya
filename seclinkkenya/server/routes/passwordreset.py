from flask import request, jsonify, current_app as app
from flask_restful import Resource
from models import User, PasswordResetToken, db
from werkzeug.security import generate_password_hash
import datetime
import secrets
from flask_mail import Message


class RequestPasswordReset(Resource):
    def post(self):
        data = request.get_json()
        email = data.get('email')

        # Check if the user exists
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'message': 'User not found'}), 404

        # Generate a unique reset token
        token = secrets.token_urlsafe(20)  # A secure random token
        expiry = datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # Token valid for 1 hour

        # Save the token in the database
        reset_token = PasswordResetToken(user_id=user.id, token=token, expiry_date=expiry)
        db.session.add(reset_token)
        db.session.commit()

        # Send reset token via email
        reset_link = f"{app.config['FRONTEND_URL']}/reset-password?token={token}"
        msg = Message('Password Reset Request', recipients=[email])
        msg.body = f"Use the following link to reset your password: {reset_link}"
        email.send(msg)

        return jsonify({'message': 'Password reset link sent to your email.'}), 200


class PasswordResetConfirm(Resource):
    def post(self):
        data = request.get_json()
        token = data.get('token')
        new_password = data.get('new_password')

        # Find the token in the database
        reset_token = PasswordResetToken.query.filter_by(token=token).first()

        if not reset_token:
            return jsonify({'message': 'Invalid or expired token'}), 400

        # Check if the token is expired
        if reset_token.expiry_date < datetime.datetime.utcnow():
            return jsonify({'message': 'Token has expired'}), 400

        # Update the user's password
        user = User.query.get(reset_token.user_id)
        user.password = generate_password_hash(new_password)
        db.session.commit()

        # Delete the token after use
        db.session.delete(reset_token)
        db.session.commit()

        return jsonify({'message': 'Password has been updated successfully.'}), 200
