from . import Request
import asyncio


def keyboard_helper(data):
	for x in ['keyboard', 'inline_keyboard', 'remove_keyboard']:
		if x in data.keys():
			if x=='keyboard': data['reply_markup'] = {x:data[x], "resize_keyboard":True}
			else: data['reply_markup'] = {x:data[x]}
			del data[x]

class sendMessage(Request):
	def __init__(self, bot, chat_id, message, **kwargs):
		keyboard_helper(kwargs)
		Request.__init__(self, bot, "sendMessage", {"chat_id":chat_id, "text":message, **kwargs})

class sendVideo(Request):
	def __init__(self, bot, chat_id, message, **kwargs):
		keyboard_helper(kwargs)
		Request.__init__(self, bot, "sendVideo", {"chat_id":chat_id, "video":message, **kwargs})

class queuedSendMessage(sendMessage):
	def __init__(self, bot, chat_id, message, **kwargs):
		sendMessage.__init__(self, bot, chat_id, message, **kwargs)
		self.result = asyncio.Future()
		self.bot.message_queue.add_message(self.data, self)
		
	async def exec(self):
		return await self.result

	def receive(self, result):
		self.result.set_result(result)

	def as_response(self):
		return None

class editMessageReplyMarkup(Request):
	def __init__(self, bot, chat_id, message_id, **kwargs):
		keyboard_helper(kwargs)
		Request.__init__(self, bot, "editMessageReplyMarkup", {"chat_id":chat_id, "message_id":message_id, **kwargs})

class editMessageText(Request):
	def __init__(self, bot, chat_id, message_id, text, **kwargs):
		keyboard_helper(kwargs)
		Request.__init__(self, bot, "editMessageText", {"chat_id":chat_id, "message_id":message_id, "text":text, **kwargs})

class deleteMessage(Request):
	def __init__(self, bot, chat_id, message_id):
		Request.__init__(self, bot, "deleteMessage", {"chat_id":chat_id, "message_id":message_id})

class answerCallbackQuery(Request):
	def __init__(self, bot, callback_query_id, **kwargs):
		Request.__init__(self, bot, "answerCallbackQuery", {"callback_query_id":callback_query_id, **kwargs})