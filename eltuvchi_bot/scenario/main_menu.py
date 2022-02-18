from config import bot
from photon import OutlineMenu, InlineMenu
from photon.objects import Message
from photon import key, act, explicit_act, reset
from dbscheme import OrderMessage

import re

from .orders import Orders
from .sold import Sold
from .stats import DailyStats, WeeklyStats
from .income import Income

class GuestMenu(OutlineMenu):
	async def _act(self):
		self.register()
		return Message("Siz bu botdan foydalanish imkonyatiga ega emassiz")


@bot.set_main_menu
class MainMenu(OutlineMenu):
	keyboard = [
		[ ("Buyurtma", act(Orders)), ("Sotdim", act(Sold)) ],
		[ ("Bugun", act(DailyStats)), ("Hisobot", act(WeeklyStats)), ("Balans", act(Income)) ],
	]
	async def _act(self, arg=None):
		if self.context.courier==None:
			return self.context.reset(GuestMenu)
		self.register()
		return Message("Bosh menyu")

	async def handle_text(self, text):
		match = re.match(r"^/id(\d*)$", text)
		if not match: return False
		order_id = int(match.group(1))
		order = self.context.dbmain.query(Order).filter(Order.id==order_id).first()
		if not order: return Message("Buyurtma serverda topilmadi")
		return self.context.act(Order, order)
		

	async def handle_message(self, message):
		if reply_to := message.reply_to_message:
			order_message = self.context.dbbot.query(OrderMessage).filter(and_(
				OrderMessage.user_id==self.user.id,
				OrderMessage.message_id==reply_to.message_id
			)).first()

			if not order_message:
				return Message("Bu buyurtma emas.")

			order = self.context.dbmain.query(Order).filter(Order.id==order_message.order_id).first()
			if not order or order.status!=1: return Message("Buyurtma serverda topilmadi")

			if not order.message: order.message = ''
			order.message += " | " + text

			metadata = dict(chat_id=self.user.id, message_id=reply_to.message_id)
			context = self.manager.find(metadata)
			await context.reset(Order, order)

			return Message("Bajarildi")

		return Message("Qayta boshlash uchun /start bosing")