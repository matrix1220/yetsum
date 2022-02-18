from ..object_dict import objectify, dictify
import requests_async as requests


import logging, json
logger = logging.getLogger('photon.bot')

def inline_button(text, callback_data = None, **kwargs):
	kwargs.update({"text":text})
	if callback_data!=None: kwargs.update({"callback_data":json.dumps(callback_data)})
	return kwargs

# class Exception(Exception):
# 	def __init__(self, description, error_code = None):
# 		super().__init__(description)
# 		self.description = description
# 		self.error_code = error_code

class Request(Exception):
	# TODO: remove args
	def __init__(self, bot, method, kwargs):
		self.bot = bot
		self.fed_data = None
		self.method = method
		self.data = kwargs

	async def exec(self):
		return await self.bot._send(self.method, self.data)

	def __await__(self):
		return self.exec().__await__()

	def as_response(self):
		return {"method":self.method, **self.data}

from . import methods

def request(bot, method, args, kwargs):
	if hasattr(methods, method):
		return getattr(methods, method)(bot, *args, **kwargs)
	else:
		return Request(bot, method, kwargs)

#import asyncio
class Bot:
	def __init__(self, token):
		self._token = token
		self.message_queue = MessageQueue(self)


	async def _send(self, method, args={}):
		logger.debug([method, args])
		result = await requests.post('https://api.telegram.org/bot' + self._token + '/' + method, json=args)
		data = objectify(result.json())
		logger.debug(data)

		if not data.ok:
			logger.error(data.description)
			raise Exception(data.description, data.error_code)
		return data.result

	async def _send_response(self, response):
		if response:
			return await self._send(response.pop('method'), response)

	async def long_polling(self, handle):
		offset = -1
		tmp = await self.getUpdates(offset=offset)
		for update in tmp:
			offset = update.update_id + 1

		while True:
			try:
				for update in await self.getUpdates(offset=offset, timeout=30):
					offset = update.update_id + 1
					try:
						if temp := await handle(update):
							await self._send_response(temp)
					except Exception as e:
						logging.exception(e)
			except Exception as e:
				logging.exception(e)

	def __getattr__(self, key):
		def function(*args, **kwargs):
			return request(self, key, args, kwargs)
		return function
		#return lambda *args, **kwargs: await Request(key, args, kwargs, self)

class QueuedMessage:
	def __init__(self, message, sender=None):
		self.message = message
		self.sender = sender
		self.next = None

# class MessagePriorityQueue:
# 	def __init__(self):
# 		self.first_message = None
# 		self.message_priorities_last = defaultdict()
# 	def add_message(self, message, priority, sender=None):
# 		queued_message = QueuedMessage(message, sender)
		
# 		if last_priority_message := self.message_priorities_last[priority]:
# 			#if last_priority_message.next != None:
# 			queued_message.next = last_priority_message.next

# 			self.message_priorities_last[priority].next = queued_message
		
# 		self.message_priorities_last[priority] = queued_message

# 		if self.first_message==None:
# 			self.first_message = queued_message

# 	def __await__(self):
# 		while True:
# 			if self.first_message==None:
# 				yield
# 				continue
# 			queued_message = self.first_message
# 			result = yield from bot._send("sendMessage", queued_message.message)
# 			if queued_message.sender!=None:
# 				queued_message.sender.receive(result)
# 			self.first_message = queued_message.next
import asyncio, time
class MessageQueue:
	def __init__(self, bot):
		self.bot = bot
		self.contains = asyncio.Future()
		self.first_message = None
		self.last_message = None

	def add_message(self, message, sender=None):
		queued_message = QueuedMessage(message, sender)
		if self.last_message!=None:
			self.last_message.next = queued_message

		self.last_message = queued_message

		if self.first_message==None:
			self.first_message = queued_message

		if not self.contains.done():
			self.contains.set_result(None)

	async def exec(self):
		counter = 0
		current_time = int(time.time())
		while True:
			await self.contains
			while self.first_message!=None:
				queued_message = self.first_message
				result = await self.bot._send("sendMessage", queued_message.message)

				if queued_message.sender!=None:
					queued_message.sender.receive(result)

				self.first_message = queued_message.next

				counter += 1

				if counter > 25:
					await asyncio.sleep(1)

				if int(time.time()) > current_time + 1:
					counter = 0
					current_time = int(time.time())

			self.contains = asyncio.Future()

	def __await__(self):
		return self.exec().__await__()