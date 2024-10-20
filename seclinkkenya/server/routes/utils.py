# from functools import wraps
# import os
# from flask import config, current_app, session, jsonify, request
# import jwt  
# from seclinkkenya.server.models import User, db
# # from flask import current_app 


# # Helper function to check if a user is logged in
# def login_required(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         if 'parent_id' not in session:
#             return jsonify({"error": "Unauthorized access, please log"}), 401
#         return f(*args, **kwargs)
#     return decorated_function

# # Token required decorator
# def token_required(f):
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         token = request.headers.get('Authorization')
        
#         if not token or not token.startswith("Bearer "):
#             return jsonify({'message': 'Token is missing or incorrect format!'}), 403
        
#         try:
#             # Extract token part from 'Bearer <token>'
#             token = token.split()[1]
#             decoded_token = jwt.decode(token, config.SECRET_KEY, algorithms=['HS256'])
#             current_user = User.query.get(decoded_token['user_id'])
#             if not current_user:
#                 return jsonify({'message': 'User not found!'}), 404
#         except jwt.ExpiredSignatureError:
#             return jsonify({'message': 'Token has expired!'}), 401
#         except jwt.InvalidTokenError:
#             return jsonify({'message': 'Invalid token!'}), 401
#         except Exception as e:
#             return jsonify({'message': f'Error processing token: {str(e)}'}), 400
        
#         return f(current_user, *args, **kwargs)
    
#     return decorated


