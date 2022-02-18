
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker as _sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///datebase.db')
sessionmaker = _sessionmaker(bind=engine)
Base = declarative_base()
session = sessionmaker()

from sqlalchemy import Integer, String, Boolean, Text, DateTime
from sqlalchemy import Column, ForeignKey

from .types import JSONEncoded, MutableObject, MutableList

from photon import User as _User

class User(Base, _User):
	__tablename__ = 'users'

	id = Column(Integer, primary_key=True)
	menu_stack = Column(MutableList.as_mutable(JSONEncoded), nullable=False, default=[])
	menu_arguments = Column(MutableObject.as_mutable(JSONEncoded))
	#language = Column(Integer)
	#blocked = Column(Boolean, default=False)

	user_id = Column(Integer)

	#@classmethod
	def find(user_id):
		user = session.query(User).filter(User.id==user_id).first()
		if not user:
			user = User(id=user_id)
			session.add(user)
			session.commit()

		return user

Base.metadata.create_all(engine)

from enum import IntEnum
class AdType(IntEnum):
	text = 1
	video = 2

class Ad(Base):
	__tablename__ = 'ads'

	id = Column(Integer, primary_key=True)
	name = Column(String)
	offer_id = Column(Integer)
	#data = Column(MutableObject.as_mutable(JSONEncoded))
	type = Column(Integer)
	caption = Column(String)
	data = Column(Integer)
