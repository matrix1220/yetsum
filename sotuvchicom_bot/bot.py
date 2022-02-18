from config import db, bot
from dbscheme import User
import photon, scenario
from dbscheme2 import session2

# import re
# from dbscheme2 import session2, Stream
# from dbscheme import Ad, AdType
# session = db.session

async def handle(update):
	try:
		_response = await photon.handle(update) # photon.handle
	finally:
		db.session.commit()
		session2.commit()
	return _response

# async def main(update):
# 	if message := update.message:
# 		chat = message.chat
# 		if chat.type == "private":
# 			user = User.find(chat.id)

# 			if user.empty_menu(): 
# 				return await user.main_menu()

# 			if text := message.text:
# 				if text == "/start":
# 					return await user.main_menu()

					
# 				return await user.handle_text(text)
# 			elif video := message.video:
# 				return await user.handle_video(video)

# 	elif callback_query := update.callback_query:
# 		user = User.find(callback_query['from'].id)
# 		if not user:
# 			return bot.answerCallbackQuery(callback_query.id)
# 		return await user.handle_callback(callback_query)


