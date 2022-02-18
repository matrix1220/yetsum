
from sqlalchemy import Integer, String, Boolean, Text, DateTime, Numeric
from sqlalchemy import ForeignKey, PrimaryKeyConstraint, ForeignKeyConstraint
from sqlalchemy.types import VARCHAR, BIGINT
from sqlalchemy.orm import relationship
from sqlalchemy import Column

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

class Courier(Base):
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
	limet = 		Column(Integer)
	store_id = 		Column(Integer)


class Offer(Base):
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


class Order(Base):
	__tablename__ = 'orders'
	id = 			Column(Integer, primary_key=True)
	user_id = 		Column(Integer)

	#stream_id = 	Column(Integer)

	offer_id = 		Column(Integer, ForeignKey('offers.id'))
	offer =			relationship("Offer")
	relationship("Child", back_populates="parent", uselist=False)
	#template_id = 	Column(Integer)
	name = 			Column(String)
	paid = 			Column(Integer)
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
	region =		relationship("Region")
	district_id = 	Column(Integer, ForeignKey('districts.id'))
	district =		relationship("District")
	message = 		Column(String)
	phone = 		Column(String)
	secondary_phone = Column(String)
	ip = 			Column(Integer)
	courier = 		Column(Integer)
	operator = 		Column(Integer, ForeignKey('cooperators.id'))
	hash = 			Column(String)

class OrderView(Base):
	__tablename__ = 'order_views'
	id = 			Column(Integer, primary_key=True)
	order_id = 		Column(Integer)
	entity_type = 	Column(Integer)
	entity_id = 	Column(Integer)
	date_time = 	Column(DateTime)

	#offer_id = 		Column(Integer, ForeignKey('offers.id'))
	#offer =			relationship("Offer")


class District(Base):
	__tablename__ = 'districts'
	id = 			Column(Integer, primary_key=True)
	name = 			Column(String)
	region_id = 	Column(Integer, ForeignKey('regions.id'))
	region =		relationship("Region", back_populates="districts")

class Region(Base):
	__tablename__ = 'regions'
	id = 			Column(Integer, primary_key=True)
	name = 			Column(String)
	districts =		relationship("District", back_populates="region")

class OrderHistory(Base):
	__tablename__ = 'orders_history'
	id = 			Column(Integer, primary_key=True)
	order_id = 		Column(Integer)
	courier_id = 	Column(Integer)
	changed_at = 	Column(Integer)
	status = 		Column(Integer)

class Cooperator(Base):
	__tablename__ = 'cooperators'
	id = 			Column(Integer, primary_key=True)
	name = 			Column(String)
	phone = 		Column(String)
	telegram_id = 	Column(String)
	password = 		Column(String)
	#money = 		Column(Integer)
	wallet = 		Column(String)
	offers = 		Column(String)

class Product(Base):
	__tablename__ = 'products'
	id = 			Column(Integer, primary_key=True)
	name = 			Column(String)
	offer = 		relationship("Offer", uselist=False, back_populates="product")
	#price = 		Column(Integer)
	store = 		Column(Integer)

	# for i in ['01', 10, 20, 25, 30, 40, 50, 60, 70, 75, 80, 85, 95]:
	# 	exec(f"store{i} = Column(Integer)")

class ProductStore(Base):
	__tablename__ = 'products_stores'
	id = 			Column(Integer, primary_key=True)
	product_id = 	Column(Integer)
	store_id =	 	Column(Integer)
	amount =	 	Column(Integer)
	#offer = 		relationship("Offer", uselist=False, back_populates="product")

#base.metadata.create_all(db.engine)