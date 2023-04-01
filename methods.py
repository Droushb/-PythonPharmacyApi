import json
from sqlalchemy import BLOB, select
from main import User, Status, Drug, Order, OrderDetails
from models import session

#drugs
def get_drugs():
    AllDrugs = session.execute(select(Drug))
    drugs = AllDrugs.scalars().all()
    result = []
    for drug in drugs:
        status = session.query(Status).filter_by(idStatus = drug.idStatus).one()
        drugJSON = {
            "Id": drug.idDrug,
            "Name": drug.Name,
            "Description": drug.Description,
            "Image": drug.Image,
            "Price": drug.Price,
            "Status": status.Name
        }
        result.append(drugJSON)
    return json.dumps(result)


def get_drug_byid(id):
    drug = session.query(Drug).filter_by(idDrug = id).one()
    status = session.query(Status).filter_by(idStatus = drug.idStatus).one()
    drugJSON = {
        "Id": drug.idDrug,
        "Name": drug.Name,
        "Description": drug.Description,
        "Image": drug.Image,
        "Price": drug.Price,
        "Status": status.Name
    }
    return json.dumps(drugJSON)

def post_drug(name, description, image, price, idStatus):
    addeddrug = Drug(Name=name, Description=description, Image=image, Price=price, idStatus=idStatus)
    session.add(addeddrug)
    session.commit()
    return 'Added a Drug with id %s' % addeddrug.idDrug + get_drug_byid(addeddrug.idDrug)

def update_drug(id, name, description, image, price, idStatus):
    updatedDrug = session.query(Drug).filter_by(idDrug = id).one()
    if name!='':
       updatedDrug.Name = name
    if description!='':
        updatedDrug.Description = description
    if image!='':
        updatedDrug.Image = image
    if price!='':
       updatedDrug.Price = price
    if idStatus!='':
       updatedDrug.idStatus = idStatus
    session.add(updatedDrug)
    session.commit()
    return 'Updated a Drug with id %s' % id + get_drug_byid(id)

def delete_drug(id):
    drugToDelete = session.query(Drug).filter_by(idDrug = id).one()
    session.delete(drugToDelete)
    session.commit()
    return 'Removed Drug with id %s' % id

#orders
def get_orders():
    AllOrders = session.execute(select(Order))
    orders = AllOrders.scalars().all()
    result = ""
    for order in orders:
        user = session.query(User).filter_by(idUser = order.idUser).one()
        status = session.query(Status).filter_by(idStatus = order.idStatus).one()
        orderJSON = {
            "Id": order.idOrder,
            "Email": user.Email,
            "Status": status.Name
        }
        result+= json.dumps(orderJSON)
    return result

def get_order_byid(id):
    order = session.query(Order).filter_by(idOrder = id).one()
    user = session.query(User).filter_by(idUser = order.idUser).one()
    status = session.query(Status).filter_by(idStatus = order.idStatus).one()
    orderDetails = session.query(OrderDetails).filter_by(idOrder = id)

    orderDetailsString = ""
    for i in orderDetails:
        drug = session.query(Drug).filter_by(idDrug = i.idDrug).one()
        orderdetailsJSON = {
            "Drug Name": drug.Name,
            "Quantity": i.quantity
        }
        orderDetailsString+= json.dumps(orderdetailsJSON)+" , "
    orderJSON = {
        "Id": order.idOrder,
        "Email": user.Email,
        "Status": status.Name
    }
    return json.dumps(orderJSON)+" , "+orderDetailsString

def post_order(idUser, idStatus, items):
    addedorder = Order(idUser=idUser, idStatus=idStatus)
    session.add(addedorder)
    session.commit()
    id = addedorder.idOrder
    for item in items:
        addedorderdetails = OrderDetails(idOrder=id, idDrug=item['idDrug'], quantity=item['quantity'])
        session.add(addedorderdetails)
    session.commit()
    return 'Added a Order with id %s' % id + get_order_byid(id)

def delete_order(id):
    orderToDelete = session.query(Order).filter_by(idOrder = id).one()
    while session.query(OrderDetails).filter_by(idOrder = id).first() is not None:
        orderDetailsToDelete =  session.query(OrderDetails).filter_by(idOrder = id).first()
        session.delete(orderDetailsToDelete)
    session.delete(orderToDelete)
    session.commit()
    return 'Removed Order with id %s' % id

#status
def get_status():
    AllStatuses = session.execute(select(Status))
    statuses = AllStatuses.scalars().all()
    result = ""
    for status in statuses:
        orderJSON = {
            "Id": status.idStatus,
            "Name": status.Name,
        }
        result+= json.dumps(orderJSON)
    return result

#users
def get_user_byEmail(email):
    userOne = session.query(User).filter_by(Email = email).one()
    userJSON = {
        "Id": userOne.Email,
        "Email": userOne.Email,
        "First Name": userOne.FirstName,
        "Last Name": userOne.LastName,
        "Password": userOne.Password,
        "Phone": userOne.Phone,
        "Role": userOne.Role
    }
    return json.dumps(userJSON)

def post_user(firstName, lastName, email, password, phone, role):
    addeduser = User(FirstName=firstName, LastName=lastName,
    Email=email, Password=password, Phone=phone, Role=role)
    session.add(addeduser)
    session.commit()
    return 'Added a User with id %s' % addeduser.idUser + get_user_byEmail(email)

def update_user(firstName, lastName, email, password, phone):
    updatedUser = session.query(User).filter_by(Email = email).first()
    if firstName!='':
        updatedUser.FirstName = firstName
    if lastName!='':
        updatedUser.LastName = lastName
    if password!='':
        updatedUser.Password = password
    if phone!='':
        updatedUser.Phone = phone
    session.add(updatedUser)
    session.commit()
    return 'Updated a User with Email %s' % email + get_user_byEmail(email)

def delete_user(email):
    userToDelete = session.query(User).filter_by(Email = email).one()
    session.delete(userToDelete)
    session.commit()
    return 'Removed User with Email %s' % email
