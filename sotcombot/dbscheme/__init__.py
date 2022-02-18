from sqlalchemy import Integer, String, Boolean, Text, DateTime
from sqlalchemy import Column, ForeignKey

from config import db, sotcom
Base = db.base

from sotcom import SotCom

from .types import JSONEncoded, MutableObject, MutableList

from photon import User as _User

class User(Base, _User):
	__tablename__ = 'users'

	id = Column(Integer, primary_key=True)
	menu_stack = Column(MutableList.as_mutable(JSONEncoded), nullable=False, default=[])
	menu_arguments = Column(MutableObject.as_mutable(JSONEncoded))
	blocked = Column(Boolean, default=False)
	last_message_time = Column(Integer, nullable=False, default=0)


	courier_id = Column(Integer)
	name = Column(String)
	token = Column(String)
	filters = Column(MutableObject.as_mutable(JSONEncoded))

	#classmethod
	def find(user_id):
		user = db.session.query(User).filter(User.id==user_id).first()
		if not user:
			user = User(id=user_id, courier_id = 0)
			db.session.add(user)
			user.check()
		else:
			user.sotcom = SotCom(user.token)
		
		return user

	def check(user):
		courier = sotcom.get.Courier(telegram_id=user.id)
		if courier:
			user.courier_id = courier.id
			user.token = courier.token
			user.name = courier.name
			user.sotcom = SotCom(courier.token)
			#user.filters = user.sotcom.get.Filters()
		else:
			user.courier_id = 0
			user.menu = None

		return courier


class OrderMessage(Base):
	__tablename__ = 'order_messages'

	id = Column(Integer, primary_key=True)
	user_id = Column(Integer)
	message_id = Column(Integer)
	order_id = Column(Integer)