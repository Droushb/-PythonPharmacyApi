import flask
import pytest
from flask_jwt_extended import (decode_token)
from requests import app
from main import User, Status, Drug, Order, OrderDetails
from requests import *
from models import session

app.testing = True
client = app.test_client()

#access_token='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImRyb3VzaC5iQGdtYWlsLmNvbSIsInBhc3N3b3JkIjoicGFzc3dvcmQifQ.lAAFddY9PICDPU4QBm6687q6aLjZIsKaRoWx0zVgt2o'
access_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY2OTE5NjkwNiwianRpIjoiNGNmNDQ4OTgtNTAwMi00NzY1LWE3YjAtYWE5MGY1NzE4YjljIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6ImFkbWluX3VzZXIiLCJuYmYiOjE2NjkxOTY5MDYsImV4cCI6MTY2OTIxMTMwNiwiaXNfYWRtaW5pc3RyYXRvciI6dHJ1ZX0.0nuuNt8WEVxxTNgM0TRHdEGsyuaqD-eUWntCTUggiZg"
id=100
invalid_id=-1
#user
@pytest.fixture(scope="function")
def default_access_token(app):
    with app.test_request_context():
        return {
            "jti": "1234",
            "type": "access",
            "fresh": True,
            "csrf": "abcd"
        }

test_user = {
    "id": 100,
    "userName": "i_nastia_13",
    "firstName": "Anastasia",
    "secondName": "Viaznikova",
    "email": "i_nastia_13@gmail.com",
    "password": "password3",
    "phone": "380967777777",
    "role": "user"
}

test_admin_user = {
    "email": "droush.b@gmail.com",
    "password": "password"
}

def test_registr_user():
    response = client.post('/register', json=test_user)
    assert response.status_code == 200

    token = json.loads(response.data.decode('utf8'))['access_token']
    with app.test_request_context():
        decoded = decode_token(token)

        assert decoded["jti"] is not None
        assert decoded["jti"] not in blacklist
        assert decoded["type"] == "access"


def test_login_user():
    response = client.post('/login', json=test_admin_user)
    assert response.status_code == 200

    global access_token
    access_token = json.loads(response.data.decode('utf8'))['access_token']
    with app.test_request_context():
        decoded = decode_token(access_token)

        assert decoded["jti"] is not None
        assert decoded["jti"] not in blacklist
        assert decoded["type"] == "access"

def test_login_without_credentials():
    response = client.get('/login')
    assert response.status_code == 405

def test_login_without_password():
    response = client.get('/login', json = {'email': "droush.b@gmail.com"})
    assert response.status_code == 405

def test_get_user_by_username():
    response = client.get(f"/user/{test_user['userName']}", headers={"Authorization": "Bearer {}".format(access_token)})
    assert response.status_code == 200
    assert json.loads(response.data.decode('utf8'))['Email'] == test_user["email"]

def test_update_user():
    user = session.query(User).filter_by(idUser = id).one()
    response = client.put(f"/user/{test_user['userName']}?phone={'0962894555'}", headers={"Authorization": "Bearer {}".format(access_token)})
    assert response.status_code == 200

def test_delete_user():
    response = client.delete(f"/user/{test_user['userName']}", headers={"Authorization": "Bearer {}".format(access_token)})
    assert response.status_code == 200
    assert session.query(User).filter_by(UserName = test_user['userName']).first() is None

#drugs
def test_get_all_drugs():
    response = client.get("/drugs", headers={"Authorization": "Bearer {}".format(access_token)})
    assert response.status_code == 200
    # assert isinstance(response.json, list)
    # res=json.loads(json.dumps(response.data.decode('utf-8')))
    # arrOfJsons=res.split("}{")
    # numOfRowsInTable = session.query(Drug).count()
    # assert numOfRowsInTable==len(arrOfJsons)

test_drug = {
    "id": 100,
    "name": "Eofilin",
    "price": 99,
    "idStatus": 3
}

def test_post_drug():
    response = client.post("/drug", json=test_drug, headers={"Authorization": "Bearer {}".format(access_token)})
    drug = session.query(Drug).filter_by(idDrug = id).one()
    assert response.status_code == 200
    assert drug is not None
    assert drug.Name == test_drug["name"]

def test_get_drug_by_id():
    response = client.get(f"/drug/{id}", headers={"Authorization": "Bearer {}".format(access_token)})
    assert response.status_code == 200
    assert json.loads(response.data.decode('utf8'))['Name'] == test_drug["name"]

def test_invalid_get_drug_by_id():
    response = client.get(f"/drug/{invalid_id}", headers={"Authorization": "Bearer {}".format(access_token)})
    assert response.status_code == 404

def test_put_drug():
    response = client.put(f"/drug/100?{'price'}={100}", headers={"Authorization": "Bearer {}".format(access_token)})
    assert response.status_code == 200

def test_delete_drug():
    response = client.delete(f"/drug/{id}", headers={"Authorization": "Bearer {}".format(access_token)})
    assert response.status_code == 200
    assert session.query(Drug).filter_by(idDrug = id).first() is None

#orders
def test_get_all_orders():
    response = client.get("/orders", headers={"Authorization": "Bearer {}".format(access_token)})
    # res=json.loads(json.dumps(response.data.decode('utf-8')))
    # arrOfJsons=res.split("}{")
    # numOfRowsInTable = session.query(Order).count()
    assert response.status_code == 200
    # assert numOfRowsInTable==len(arrOfJsons)

test_order = {
    "id": 100,
    "idUser": 1,
    "idStatus": 4,
    "items": [
        {
            "idDrug": 2,
            "quantity": 8
        },
        {
            "idDrug": 3,
            "quantity": 8
        }
    ]
}

def test_post_order():
    response = client.post(f'/order', json=test_order, headers={"Authorization": "Bearer {}".format(access_token)})
    order = session.query(Order).filter_by(idOrder = id).one()
    assert response.status_code == 200
    assert order.idUser== 1

def test_get_order_by_id():
    response = client.get(f'/order/{id}', headers={"Authorization": "Bearer {}".format(access_token)})
    result=json.loads(json.dumps(response.data.decode('utf-8')))
    arrOfJsons=result.split(" , ")
    user = session.query(User).filter_by(idUser = 1).one()
    assert response.status_code == 200
    assert user is not None
    assert json.loads(arrOfJsons[0])['UserName'] == user.UserName

def test_invalid_get_order_by_id():
    response = client.get(f'/order/{invalid_id}', headers={"Authorization": "Bearer {}".format(access_token)})
    assert response.status_code == 404

def test_delete_order():
    response = client.delete(f"/order/{id}", headers={"Authorization": "Bearer {}".format(access_token)})
    assert response.status_code == 200
    assert session.query(Order).filter_by(idOrder = id).first() is None

#statuses
def test_get_all_statuses():
    response = client.get("/statuses", headers={"Authorization": "Bearer {}".format(access_token)})
    numOfRowsInTable = session.query(Status).count()
    res=json.loads(json.dumps(response.data.decode('utf-8')))
    arrOfJsons=res.split("}{")
    assert response.status_code == 200
    assert numOfRowsInTable==len(arrOfJsons)

def test_logout_user():
    response = client.delete('/logout', headers={"Authorization": "Bearer {}".format(access_token)})
    assert response.status_code == 200
    with app.test_request_context():
        decoded = decode_token(access_token)
        assert decoded["jti"] in blacklist

# with app.test_request_context('/drug/1'):
#     assert flask.request.args['Name'] == 'Noshpa'
# def test_get_all_books():
#     response = app.test_client().get('/drug/1')
#     res = json.loads(response.data.decode('utf-8')).get("Drugs")
#     assert res[0]['Name'] == 'Noshpa'

