from sqlalchemy import Integer, String, Boolean, Text, DateTime, Numeric, Decimal
from sqlalchemy import ForeignKey, PrimaryKeyConstraint, ForeignKeyConstraint
from sqlalchemy.types import VARCHAR, BIGINT
from sqlalchemy.orm import relationship
from sqlalchemy import Column

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker as _sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import os.path
debug = os.path.exists("debug")

if debug:
	engine = create_engine('mysql+mysqlconnector://matrix1220@localhost/sotcom')
else:
	engine = create_engine('mysql+mysqlconnector://sotuvchi_api:123456@10.0.0.4/sotuvchi_new')


sessionmaker = _sessionmaker(bind=engine)
session2 = sessionmaker()
base = declarative_base()

class Courier(base):
	__tablename__ = 'couriers'
	id = 			Column(Integer, primary_key=True)
	name = 			Column(String) 				
	phone = 		Column(String)				
	telegram_id = 	Column(Integer)		
	status = 		Column(Integer)
	money = 		Column(Integer)
	pay_for = 		Column(Integer)
	#region = 		Column(String)
	regions = 		Column(String)
	districts = 	Column(String)
	token = 		Column(String)
	store = 		Column(String)

class User(base):
	__tablename__ = 'users'
	id = 			Column(Integer, primary_key=True)
	name = 			Column(String)
	telegram_id = 	Column(Integer)
	money = 	Column(Decimal)


class Offer(base):
	__tablename__ = 'offers'
	id = 			Column(Integer, primary_key=True)
	product_id = 	Column(Integer, ForeignKey('products.id'))
	product =		relationship("Product", back_populates="offer")
	image = 		Column(String)
	name = 			Column(String)
	short_name = 	Column(String)
	cat = 			Column(Integer)
	type = 			Column(Integer)
	added = 		Column(Integer)
	price = 		Column(Integer)
	pay_for = 		Column(Integer)
	product_link = 	Column(String)


class Order(base):
	__tablename__ = 'orders'
	id = 			Column(Integer, primary_key=True)
	user_id = 		Column(Integer)
	#stream_id = 	Column(Integer)
	offer_id = 		Column(Integer)
	#template_id = 	Column(Integer)
	name = 			Column(String)
	#paid = 		Column(Integer)
	#date_time = 	Column(Integer)
	date = 			Column(Integer)
	date_time = 	Column(Integer)
	quantity = 		Column(String)
	money = 		Column(Integer)
	cost = 			Column(String)
	status = 		Column(Integer)
	#deleted_at = 	Column(Integer)
	#region = 		Column(String)
	region_id = 	Column(Integer, ForeignKey('regions.id'))
	region =		relationship("Regions")
	district_id = 	Column(Integer, ForeignKey('districts.id'))
	district =		relationship("Districts")
	message = 		Column(String)
	phone = 		Column(String)
	ip = 			Column(Integer)
	courier = 		Column(Integer)
	operator = 		Column(Integer)
	hash = 			Column(String)

class Districts(base):
	__tablename__ = 'districts'
	id = 			Column(Integer, primary_key=True)
	name = 			Column(String)
	region_id = 	Column(Integer, ForeignKey('regions.id'))
	region =		relationship("Regions", back_populates="districts")

class Regions(base):
	__tablename__ = 'regions'
	id = 			Column(Integer, primary_key=True)
	name = 			Column(String)
	districts =		relationship("Districts", back_populates="region")

class OrderHistory(base):
	__tablename__ = 'orders_history'
	id = 			Column(Integer, primary_key=True)
	order_id = 		Column(Integer)
	courier_id = 	Column(Integer)
	changed_at = 	Column(Integer)
	status = 		Column(Integer)

class Cooperator(base):
	__tablename__ = 'cooperators'
	id = 			Column(Integer, primary_key=True)
	name = 			Column(String)
	phone = 		Column(String)
	telegram_id = 	Column(String)
	password = 		Column(String)
	#money = 		Column(Integer)
	wallet = 		Column(String)
	offers = 		Column(String)

class Product(base):
	__tablename__ = 'products'
	id = 			Column(Integer, primary_key=True)
	name = 			Column(String)
	offer = 		relationship("Offer", uselist=False, back_populates="product")
	#price = 		Column(Integer)
	store = 		Column(Integer)

	for i in ['01', 10, 20, 25, 30, 40, 50, 60, 70, 75, 80, 85, 95]:
		exec(f"store{i} = Column(Integer)")

class Stream(base):
	__tablename__ = 'streams'
	id = 			Column(Integer, primary_key=True)
	user_id = 		Column(Integer)
	template_id = 	Column(Integer)
	offer_id = 		Column(Integer, ForeignKey('offers.id'))
	offer = 		relationship("Offer")
	name = 			Column(String)
	url = 			Column(String)
	status = 		Column(Integer)

#base.metadata.create_all(db.engine)

def row_as_dict(row):
	# result = {}
	# for column in row.__table__.columns:
	# 	#value = getattr(row, column.key)
	# 	result[column.key] = getattr(row, column.key)

	# return result
	return dict((column.key, getattr(row, column.key)) for column in row.__table__.columns)