from config import bot, db, sotcom, least_handlers_time
from dbscheme import User
from sotcom import SotCom

import photon, scenario, json, time

async def handle(update):
	try:
		_response = await main(update)
	finally:
		db.session.commit()
	return _response


async def main(update):
	if (message := update.message) and (message.chat.type == "private"):
		chat = message.chat
		user = User.find(chat.id)
		user.update = update

		if not user.last_message_time or user.last_message_time < least_handlers_time:
			user.last_message_time = int(time.time())
			return await user.main_menu()

		if text := message.text:
			print("test 1")
			if text == "/start":
				if user.check():
					return await user.main_menu()

			if not user.courier_id: return

			if user.empty_menu(): 
				return await user.main_menu()

			return await user.handle_text(text)


	elif (callback_query := update.callback_query) and (data := callback_query.data):
		if callback_query.message.date < least_handlers_time:
			return await bot.answerCallbackQuery(callback_query.id, text='expired')
		data = json.loads(data)
		user = User.find(callback_query['from'].id)
		if not user.courier_id:
			return await bot.answerCallbackQuery(callback_query.id)

		return await user.handle_callback(callback_query)



