from flask import request, jsonify
from flask_restful import Resource
from models import db, Notification, User  
from datetime import datetime

# Notification Model 
class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipient = db.relationship('User', back_populates='notifications')

    def __init__(self, message, recipient_id):
        self.message = message
        self.recipient_id = recipient_id

    def to_dict(self):
        return {
            'id': self.id,
            'message': self.message,
            'created_at': self.created_at.isoformat(),
            'recipient_id': self.recipient_id,
        }

# API Resource for Notifications
class NotificationResource(Resource):
    def get(self, user_id):
        user = User.query.get_or_404(user_id)
        notifications = user.notifications
        return jsonify([notification.to_dict() for notification in notifications]), 200

    def post(self):
        data = request.get_json()
        message = data.get('message')
        recipient_id = data.get('recipient_id')

        if not message or not recipient_id:
            return jsonify({'error': 'Message and recipient ID are required.'}), 422

        notification = Notification(message=message, recipient_id=recipient_id)
        db.session.add(notification)
        db.session.commit()

        return jsonify(notification.to_dict()), 201

    def delete(self, notification_id):
        notification = Notification.query.get_or_404(notification_id)
        db.session.delete(notification)
        db.session.commit()
        return '', 204
