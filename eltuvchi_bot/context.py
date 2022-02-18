
from config import bot_session_maker, main_session_maker

from dbscheme import User, Message
from dbsite import Courier

from photon import ContextManager as ContextManager_
#from photon import Context as Context_
from photon import OutlineMenuContext as OutlineMenuContext_
from photon import InlineMenuContext as InlineMenuContext_

from photon import MenuStack

class InlineMenuContext(InlineMenuContext_):
	def set_message_id(self, message_id):
		self.message.message_id = self.metadata['message_id']
		self.dbbot.add(self.message)
		#self.dbbot.commit()

	def commit(self):
		super().commit()
		self.dbmain.commit()
		self.dbbot.commit()

class OutlineMenuContext(OutlineMenuContext_):
	def commit(self):
		super().commit()
		self.dbmain.commit()
		self.dbbot.commit()

#db.commit()
class ContextManager(ContextManager_):
	def find_inline(self, metadata):
		dbbot = bot_session_maker()
		dbmain = main_session_maker()
		chat_id = metadata['chat_id']

		courier = dbmain.query(Courier).filter_by(telegram_id=chat_id).first()
		if not courier: return

		if metadata['message_id']:
			message = dbbot.query(Message).filter_by(
				chat_id=chat_id,
				message_id=metadata['message_id'],
			).first()
		else:
			message = None

		if not message:
			message = Message(
				chat_id=chat_id,
				message_id=metadata['message_id'],
			)
			if metadata['message_id']:
				dbbot.add(message)
				#dbbot.commit()

			
		context = self.instantiate(InlineMenuContext, metadata)
		context.dbbot = dbbot
		context.dbmain = dbmain
		context.message = message
		context.courier = courier
		context.menu_stack = MenuStack(message.menu_stack)
		context.keyboard = message.keyboard

		return context

	def find_outline(self, metadata):
		dbbot = bot_session_maker()
		dbmain = main_session_maker()
		chat_id = metadata['chat_id']

		courier = dbmain.query(Courier).filter_by(telegram_id=chat_id).first()
		if not courier: return

		user = dbbot.query(User).filter_by(id=chat_id).first()
		if not user:
			user = User(id=chat_id)
			dbbot.add(user)			
			#dbbot.commit()

		context = self.instantiate(OutlineMenuContext, metadata)
		context.dbbot = dbbot
		context.dbmain = dbmain
		context.user = user
		context.courier = courier
		context.menu_stack = MenuStack(user.menu_stack)
		context.keyboard = user.keyboard

		return context
		
	# def save(self, context):
	# 	context.dbbot.commit()
	# 	context.dbmain.commit()