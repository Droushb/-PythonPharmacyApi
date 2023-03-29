import bcrypt
from flask import Flask, request
from methods import *
from flask_jwt_extended import (JWTManager, create_access_token, get_jwt, verify_jwt_in_request, jwt_required)
from functools import wraps
from datetime import timedelta
from sqlalchemy.exc import IntegrityError, NoResultFound
from flask_cors import CORS
from main import User
import pytest

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = 'd5fb8c4fa8bd46638dadc4e751e0d68d'
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=4)
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
CORS(app)

jwt = JWTManager(app)

blacklist = set()
@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(some, decrypted_token):
    jti = decrypted_token['jti']
    return jti in blacklist


def check_if_token_is_revoked(some, token):
    jti = token["jti"]
    token_in_redis = blacklist.get(jti)
    return token_in_redis is not None

def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            try:
                if claims["is_administrator"]:
                    return fn(*args, **kwargs)
                else:
                    return "Admins only!", 403
            except KeyError:
                return "Admins only!", 403
        return decorator
    return wrapper


#DRUGS
@app.route('/drugs', methods = ['GET'])
@jwt_required()
def drugs_get():
	try:
		return get_drugs()
	except NoResultFound:
		return "Drugs not found", 404

@app.route('/drug/<id>', methods = ['GET'])
@jwt_required()
def drug_get_byid(id):
	try:
		return get_drug_byid(id)
	except NoResultFound:
		return "Drug not found", 404

@app.route('/drug', methods = ['POST'])
@admin_required()
def drug_post():
	try:
		id = request.json.get('id', None)
		name = request.json.get('name', None)
		price = request.json.get('price', None)
		idStatus = request.json.get('idStatus', None)
		if id=='':
			return 'Missing id', 400
		if name=='':
			return 'Missing name', 400
		if price=='':
			return 'Missing price', 400
		if idStatus=='':
			return 'Missing idStatus', 400
		return post_drug(id, name, price, idStatus)
	except IntegrityError:
		return 'Drug Already Exists', 400

@app.route('/drug/<id>', methods = ['PUT'])
@admin_required()
def drug_update(id):
	name = request.args.get('name', '')
	price = request.args.get('price', '')
	idStatus = request.args.get('idStatus', '')
	return update_drug(id, name, price, idStatus)

@app.route('/drug/<id>', methods = ['DELETE'])
@admin_required()
def drug_delete(id):
	try:
		return delete_drug(id)
	except NoResultFound:
		return "Drug not found", 404

#ORDER
@app.route('/orders', methods = ['GET'])
@admin_required()
def orders_get():
	try:
		return get_orders()
	except NoResultFound:
		return "Orders not found", 404

@app.route('/order/<id>', methods = ['GET'])
@jwt_required()
def order_get_byid(id):
	try:
		return get_order_byid(id)
	except NoResultFound:
		return "Order not found", 404

@app.route('/order', methods = ['POST'])
@jwt_required()
def order_post():
		id = request.json.get('Id', None)
		idUser = request.json.get('idUser', None)
		idStatus = request.json.get('idStatus', None)
		items = request.json.get('items', None)
		if idUser=='':
			return 'Missing idUser', 400
		if idStatus=='':
			return 'Missing idStatus', 400
		return post_order(id, idUser, idStatus, items)

@app.route('/order/<id>', methods = ['DELETE'])
@jwt_required()
def order_delete(id):
	try:
		return delete_order(id)
	except NoResultFound:
		return "Order not found", 404

#STATUS
@app.route('/statuses', methods = ['GET'])
@admin_required()
def status_get():
	try:
		return get_status()
	except NoResultFound:
		return "Statuses not found", 404

#USER
@app.route('/user/<Email>', methods = ['GET'])
def user_get_byid(email):
	try:
		return get_user_byEmail(email)
	except NoResultFound:
		return "User not found", 404

@app.route('/user/<Email>', methods = ['PUT'])
@jwt_required()
def user_update(email):
	firstName = request.args.get('firstName', '')
	lastName = request.args.get('lastName', '')
	password = request.args.get('password', '')
	phone = request.args.get('phone', '')
	return update_user(firstName, lastName, email, password, phone)

@app.route('/user/<Email>', methods = ['DELETE'])
@admin_required()
def user_delete(email):
	try:
		return delete_user(email)
	except NoResultFound:
		return "User not found", 404

@app.route('/register', methods=['POST'])
def register():
	try:
		id = request.json.get('id', None)
		firstName = request.json.get('firstName', None)
		secondName = request.json.get('secondName', None)
		email = request.json.get('email', None)
		password = request.json.get('password', None)
		phone = request.json.get('phone', None)
		role = request.json.get('role', None)

		if not firstName:
				return 'Missing firstName', 400
		if not secondName:
				return 'Missing secondName', 400
		if not email:
				return 'Missing email', 400
		if not password:
				return 'Missing password', 400
		if not phone:
				return 'Missing phone', 400
		
		hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
		post_user(id, firstName, secondName, email, hashed, phone, role)

		if(role=="admin"):
			access_token = create_access_token("admin_user", additional_claims={"is_administrator": True})
		else:
			access_token = create_access_token("common_user", additional_claims={"is_user": True})
		return {"access_token": access_token}, 200
	except IntegrityError:
		session.rollback()
		return 'User Already Exists', 400
	except AttributeError:
		return 'Provide an Email and Password in JSON format in the request body', 400

@app.route('/login', methods=['POST'])
def login():
	try:
		email = request.json.get('email', None)
		password = request.json.get('password', None)
		if not email:
				return 'Missing email', 400
		if not password:
				return 'Missing password', 400

		user = session.query(User).filter_by(Email = email).one()
		if not user:
				return 'User Not Found!', 404

		if bcrypt.checkpw(password.encode('utf8'), user.Password.encode('utf8')): 
				if(user.Role=="admin"):
					access_token = create_access_token("admin_user", additional_claims={"is_administrator": True})
				else:
					access_token = create_access_token("common_user", additional_claims={"is_user": True})
				return {"access_token": access_token}, 200
		else:
				return 'Invalid Login Info!', 400
	except AttributeError:
		return 'Provide an Email and Password in JSON format in the request body', 400

@app.route("/logout", methods=["DELETE"])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    blacklist.add(jti)
    return "Logout successful"

app.run()