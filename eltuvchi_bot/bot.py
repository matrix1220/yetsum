
from config import bot, sotcom, least_handlers_time
from dbscheme import User
from sotcom import SotCom

import photon, scenario, json, time


# if not user.last_message_time or user.last_message_time < least_handlers_time:
# 	user.last_message_time = int(time.time())
# 	return await user.main_menu()

# if callback_query.message.date < least_handlers_time:
# 	return await bot.answerCallbackQuery(callback_query.id, text='expired')
