from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

from sqlalchemy import Integer, String, Boolean, Text, DateTime, JSON
from sqlalchemy import Column, ForeignKey

from sqlalchemy.ext.mutable import Mutable, MutableList, MutableDict

from sqlalchemy.types import TypeDecorator, VARCHAR
import json

class JSONEncoded(TypeDecorator):
    impl = VARCHAR

    def process_bind_param(self, value, dialect):
        if value is not None: value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None: value = json.loads(value)
        return value


class User(Base):
	__tablename__ = 'users'

	id = Column(Integer, primary_key=True)
	menu_stack = Column(MutableList.as_mutable(JSONEncoded), nullable=False)
	keyboard = Column(MutableDict.as_mutable(JSONEncoded), nullable=False)
	shared_data = Column(JSON)
	blocked = Column(Boolean, default=False)
	last_message_time = Column(Integer, nullable=False, default=0)

	courier_id = Column(Integer, default=0)
	name = Column(String)
	token = Column(String)
	#filters = Column(MutableObject.as_mutable(JSONEncoded))
	# def __new__(self, *args, **kwargs):
	# 	print(args, kwargs)
	# 	return super().__new__(self, *args, **kwargs)

	def __init__(self, menu_stack=[], keyboard={}, **kwargs):
		super().__init__(menu_stack=menu_stack, keyboard=keyboard, **kwargs)

class Message(Base): # InlineMenu
	__tablename__ = 'messages'

	chat_id = Column(Integer, primary_key=True)
	message_id = Column(Integer, primary_key=True)
	content = Column(MutableDict.as_mutable(JSONEncoded))
	menu_stack = Column(MutableList.as_mutable(JSONEncoded), nullable=False)
	keyboard = Column(MutableDict.as_mutable(JSONEncoded), nullable=False)
	#shared_data = Column(JSON)

	def __init__(self, menu_stack=[], keyboard={}, **kwargs):
		super().__init__(menu_stack=menu_stack, keyboard=keyboard, **kwargs)


class OrderMessage(Base):
	__tablename__ = 'order_messages'

	id = Column(Integer, primary_key=True)
	user_id = Column(Integer)
	message_id = Column(Integer)
	order_id = Column(Integer)
	send_at = Column(Integer)

from config import bot_database_engine
Base.metadata.create_all(bot_database_engine)