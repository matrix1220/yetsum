
from photon import OutlineMenu, InlineMenu
from photon.objects import Message
from photon import key, act, explicit_act, reset
from dbscheme import OrderMessage


class Income(InlineMenu):
	keyboard = [[ ("Kirim hisoboti", key("income")) ]]
	async def _act(self):
		self.register()
		return Message(f"Sizning qarzinggiz: {self.context.courier.money}")

	async def handle_key_income(self):
		text = "\n".join([
			"✅ Topshirilgan pullar",
			"➖➖➖➖➖➖➖➖",
			""
		])
		for income in self.context.courier.incomes.limit(15):
			text += "\n".join([
				f"💰 {income.sum}",
				f"🕐 {income.date}",
				f"💬 {income.comment}",
				""
			])
		return Message(text)