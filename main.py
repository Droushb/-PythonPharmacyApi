from xmlrpc.client import DateTime
import mysql.connector
from sqlalchemy import create_engine, Column, String, Integer, DateTime, BIGINT, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session, relationship


Pharmacy = mysql.connector.connect(
  host="localhost",
  user="root",
  database='pharmacy',
  password="MySQLpassword22!"
)


engine = create_engine('mysql://root:MySQLpassword22!@localhost:3306/pharmacy', pool_pre_ping=True)
SessionFactory = sessionmaker(bind=engine)
Session = scoped_session(SessionFactory)
Base = declarative_base()

class User(Base):
  __tablename__ = 'User'

  idUser = Column(Integer, primary_key=True, autoincrement=True)
  FirstName = Column(String(45), nullable=False)
  LastName = Column(String(45), nullable=False)
  Email = Column(String(45), unique=True)
  Password = Column(String(300), nullable=False)
  Phone = Column(String(45), nullable=False)
  Role = Column(String(45), nullable=False)

class Status(Base):
    __tablename__ = 'Status'

    idStatus = Column(Integer, primary_key=True)
    Name = Column(String(45), nullable=False)

class Drug(Base):
    __tablename__ = 'Drug'

    idDrug = Column(Integer, primary_key=True, autoincrement=True)
    Name = Column(String(45), nullable=False)
    Price =  Column(Integer, nullable=False)
    idStatus = Column(Integer, ForeignKey(Status.idStatus))
    Status = relationship(Status, backref='Drug', lazy="joined")

class Order(Base):
    __tablename__ = 'Order'

    idOrder = Column(Integer, primary_key=True, autoincrement=True)
    idUser = Column(Integer, ForeignKey(User.idUser))
    idStatus = Column(Integer, ForeignKey(Status.idStatus))

    User = relationship(User, backref='Order', lazy="joined")
    Status = relationship(Status, backref='Order', lazy="joined")

class OrderDetails(Base):
    __tablename__ = 'OrderDetails'

    idOrderDetails = Column(Integer, primary_key=True, autoincrement=True)
    idOrder = Column(Integer, ForeignKey(Order.idOrder), nullable=False)
    idDrug = Column(Integer, ForeignKey(Drug.idDrug), nullable=False)
    quantity = Column(Integer, nullable=False)

    Drug = relationship(Drug, backref='OrderDetails', lazy="joined")
    Order = relationship(Order, backref='OrderDetails', lazy="joined")

# Base.metadata.create_all(engine)

