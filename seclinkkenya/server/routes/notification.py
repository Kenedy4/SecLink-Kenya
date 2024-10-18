from flask import request, jsonify
from flask_restful import Resource
from models import Notification, db
from seclinkkenya.server.routes.auth import token_required   # type: ignore
from seclinkkenya.server.app import login_required

class Notification(Resource):
    @login_required
    @token_required
    def get(self, notification_id=None):
        if notification_id:
            notification = Notification.query.get_or_404(notification_id)
            return notification.to_dict(), 200
        notifications = Notification.query.all()
        return jsonify([notification.to_dict() for notification in notifications]), 200

    @login_required
    def post(self):
        data = request.get_json()
        notification = Notification(
            message=data.get('message'),
        )
        db.session.add(notification)
        db.session.commit()
        return notification.to_dict(), 201

    @login_required
    def delete(self, notification_id):
        notification = Notification.query.get_or_404(notification_id)
        db.session.delete(notification)
        db.session.commit()
        return '', 204