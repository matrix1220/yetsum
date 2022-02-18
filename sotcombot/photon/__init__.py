#from config import debug
#from .client import inline_button

from . import _globals

def Bot(token):
	from .client import Bot
	_globals.bot = Bot(token)
	return _globals.bot


# class Handler: pass
# class MenuHandler: pass
# class CallbackHandler: pass
# abstract_handlers = [MenuHandler, CallbackHandler]

def handler(_handler):
	_handler.id = len(handlers)
	handlers.append(_handler)
	return _handler

handlers = []
#menu_handlers = []

async def handle(update):
	if message := update.message:
		chat = message.chat
		if chat.type == "private":
			user = _globals.User.find(chat.id)

			if user.empty_menu(): 
				return await user.main_menu()

			if text := message.text:
				if text == "/start":
					return await user.main_menu()
				return await user.handle_text(text)

	elif callback_query := update.callback_query:
		user = _globals.User.find(callback_query['from'].id)
		if not user:
			return _globals.bot.answerCallbackQuery(callback_query.id)
		return await user.handle_callback(callback_query)

from .client import Request
import json

_users = {}
# Persistence
# Context
class User:
	_passes = False
	def __init__(self):
		self.menu_stack = []
		#self._passes = False

	def current_menu(self):
		if not self.empty_menu():
			return self.menu_stack[-1]
	def set_current_menu(self, menu):
		if self.empty_menu():
			self.menu_stack.append(menu)
		else:
			self.menu_stack[-1] = menu
	def pop_menu(self):
		return self.menu_stack.pop()
	def push_menu(self, menu):
		return self.menu_stack.append(menu)
	def reset_menu(self):
		self.menu_stack = []
	def empty_menu(self):
		return len(self.menu_stack)==0

	def find(user_id):
		if user_id in _users:
			return _users[user_id]
		else:
			user = User()
			_users[user_id] = user
			return user

	def __init_subclass__(cls, **kwargs):
		_globals.User = cls

	def passes(self):
		self._passes = True

	def act(self, handler):
		async def func(*args, **kwargs):
			result = await self._execute_handle(handler.act, args, kwargs)
			if not self._passes: return result
			self._passes = False
			self.push_menu([handler.id, args, kwargs])
			return result
		return func

	def explicit_act(self, handler):
		async def func(*args, **kwargs):
			result = await self._execute_handle(handler.act, args, kwargs)
			if not self._passes: return result
			self._passes = False
			self.set_current_menu([handler.id, args, kwargs])
			return result
		return func

	async def main_menu(self):
		self.reset_menu()
		return await self.explicit_act(handlers[0])()

	async def back(self):
		self.pop_menu()
		if self.empty_menu():
			return await self.main_menu()
		menu = self.current_menu()
		handler = handlers[menu[0]]
		return await self.explicit_act(handler)(*menu[1], **menu[2])
		

	async def _execute_handle(self, handle, args, kwargs={}):
		try:
			result = await handle(self, *args, **kwargs)
			if isinstance(result, Request):
				return result.as_response()
			return result
		except Request as e:
			return e.as_response()

	async def handle_text(self, text):
		handler = handlers[self.current_menu()[0]]
		return await self._execute_handle(handler.handle_text, [text])

	async def handle_callback(self, callback_query):
		if data := callback_query.data:
			data = json.loads(data)
			handler = handlers[data.pop(0)]
			return await self._execute_handle(handler.handle_callback, [callback_query, data])

_globals.User = User

import virtualmod

from .client import request
# class _methods_meta(virtualmod.VirtualModule, type):
# 	def __getattr__(self, key):
# 		def function(*args, **kwargs):
# 			return request(_globals.bot, key, args, kwargs)
# 		return function

# class methods(virtualmod.VirtualModule):
# 	__module_name__ = 'methods'
# 	def __getattr__(self, key):
# 		def function(*args, **kwargs):
# 			return request(_globals.bot, key, args, kwargs)
# 		return function

_methods = virtualmod.create_module('photon.methods')
def _tmp(key):
	def function(*args, **kwargs):
		return request(_globals.bot, key, args, kwargs)
	return function

_methods.__getattr__ = _tmp
