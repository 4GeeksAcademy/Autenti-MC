"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
from flask import Flask, request, jsonify, Blueprint
from api.models import db, User
from api.utils import generate_sitemap, APIException
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_mail import Mail, Message
from datetime import datetime, timedelta
import jwt
import uuid
from flask_bcrypt import Bcrypt

api = Blueprint('api', __name__)

# Allow CORS requests to this API
CORS(api)
bcrypt = Bcrypt()
# Configuración de Flask-Mail
mail = Mail()
def configure_mail(app):
    app.config['MAIL_SERVER'] = 'smtp.office365.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_USERNAME'] = 'cwspablo@outlook.com' #correo real y pass
    app.config['MAIL_PASSWORD'] = '4geeks4geeks'
    mail.init_app(app)

def generate_reset_token(email):
    # Payload con solo la información mínima necesaria
    payload = {
        'sub': email,  # Incluye solo el email como subject
        'exp': datetime.utcnow() + timedelta(minutes=10)  # Reduce la duración a 10 minutos para mayor seguridad
    }
    # Utiliza una clave secreta más corta
    secret_key = 'short_secret'
    return jwt.encode(payload, secret_key, algorithm='HS256')

# Decoding function remains the same
def decode_reset_token(token):
    try:
        payload = jwt.decode(token, 'short_secret', algorithms=['HS256'])
        return payload['sub']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

@api.route('/hello', methods=['POST', 'GET'])
def handle_hello():
    response_body = {
        "message": "Hello! I'm a message that came from the backend, check the network tab on the google inspector and you will see the GET request"
    }
    return jsonify(response_body), 200

@api.route('/users', methods=['GET'])
def handle_users():
    users = User.query.all()
    all_users = list(map(lambda x: x.serialize(), users))
    return jsonify(all_users), 200

@api.route('/users', methods=['POST'])
def add_user():
    request_data = request.get_json()
    if not request_data or 'email' not in request_data or 'password' not in request_data:
        raise APIException('Invalid request body', status_code=400)
    
    user_uuid = str(uuid.uuid4())
    password= request_data.get('password')
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(email=request_data['email'], password=hashed_password, user_uuid=user_uuid)

    db.session.add(new_user)
    db.session.commit()

    return jsonify(new_user.serialize())

@api.route('/login', methods=['POST'])
def create_token():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    user = User.query.filter_by(email=email).first()
   

    if user is None or not user.check_password(password):
        return jsonify({"msg" : "Invalid email or password"}), 401

    access_token = create_access_token(identity=user.id)
    return jsonify({"token": access_token, "user_id": user.id})

@api.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user_id = get_jwt_identity()
    user = User.filter.get(current_user_id)
    return jsonify({"id": user.id, "email": user.email}), 200

# Ruta para solicitar la recuperación de contraseña
@api.route('/forgot-password', methods=['POST'])
def forgot_password():
    email = request.json.get('email')
    user = User.query.filter_by(email=email).first()
    
    if user:
        user_uuid = user.user_uuid
        reset_link = f"http://127.0.0.1:3000/resetpassword/{user_uuid}"
        print(user_uuid, reset_link)
        msg = Message("Password Reset Request",
                      sender="cwspablo@outlook.com",  # Cambiar por tu correo
                      recipients=[email])
        msg.body = f"To reset your password, visit the following link: {reset_link}"
        mail.send(msg)
        
        return jsonify({"msg": "Password reset link sent"}), 200
    
    return jsonify({"msg": "Email not found"}), 404

@api.route('/reset-password', methods=['PUT'])
def recovery_password():
    data = request.get_json(force=True)
    try:
        user_uuid = data.get('user_uuid') 
        new_password = data.get('password')
        user = User.query.filter_by(user_uuid=user_uuid).first()
        hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        print (data, "dataa")
        print(user)
        print(user_uuid, "user_uuid")
        print(new_password)
        if user:
            user.password = hashed_password
            db.session.commit()
            return jsonify({"message": "Usuario confirmado exitosamente"}), 200
        else:
            return jsonify({"error": "Usuario no encontrado"}), 404
    except Exception as e:
        return jsonify({"error": f"Error al confirmar el usuario: {str(e)}"}), 500
