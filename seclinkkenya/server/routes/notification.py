# from flask import request, jsonify
# from flask_restful import Resource
# from models import Notifications, db
# from utils import token_required, login_required  # type: ignore


# class Notifications(Resource):
#     @login_required
#     @token_required
#     def get(self, notification_id=None):
#         if notification_id:
#             notification = Notifications.query.get_or_404(notification_id)
#             return notification.to_dict(), 200
#         notifications = Notifications.query.all()
#         return jsonify([notification.to_dict() for notification in notifications]), 200

#     @login_required
#     def post(self):
#         data = request.get_json()
#         notification = Notifications(
#             message=data.get('message'),
#         )
#         db.session.add(notification)
#         db.session.commit()
#         return notification.to_dict(), 201

#     @login_required
#     def delete(self, notification_id):
#         notification = Notifications.query.get_or_404(notification_id)
#         db.session.delete(notification)
#         db.session.commit()
#         return '', 204