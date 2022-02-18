from config import bot, status_channel, status_

from photon import key, act, explicit_act, reset, back
from photon import OutlineMenu, InlineMenu
from photon.objects import Message
from photon.client import inline_button

from dbscheme import OrderMessage
from dbsite import OrderHistory, ProductStore, OrderView, Order as Order_
import datetime
import decimal



async def remove_orders(dbbot, **filters):
	for order_message in dbbot.query(OrderMessage).filter_by(**filters):
		try:
			await bot.deleteMessage(order_message.user_id, order_message.message_id)
		except:
			pass
		#dbbot.delete(order_message)

	dbbot.query(OrderMessage).filter_by(**filters).delete()

def format_order(order, show=True):
	return "\n".join([
		f"👤 {order.name}",
		f"📱 {order.phone if show else f'+998 *** {order.phone[-2:]}'}",
		f"☎️ {order.secondary_phone if show else f'+998 *** {order.secondary_phone[-2:]}'}",
		f"🛍 {order.quantity} dona {order.offer.short_name}, {order.cost} so'm",
		f"",
		f"🏘 {order.region.name}, #{order.district.name}. {order.message}",
		f"🕥 {order.date_time}, 👮 {order.cooperator.name if order.cooperator else '?'}",
	])
	
class Order(InlineMenu):
	def _init(self, order=None, order_id=None):
		if order:
			order_id = order.id

		#if not order_id: raise Exception("cant")

		self.order_id = order_id
		self.order = order

		super()._init(order_id=order_id)
		self.show = None
		
		if self.order:
			self.show = True if order.courier_id==self.context.courier.id else False

	def _get_order(self):
		if order: return
		order = dbmain.query(Order_).filter(Order_.id==self.order_id).first()
		#if not order or order.status!=1: return "Xatolik yuzberdi"


	def text_(self):
		return format_order(self.order, self.show)

	def keyboard_(self):
		if self.show:
			keyboard = [[
				(y, key("status", x))
					for x, y in status_.items()
			]]
		else:
			keyboard = [[ ("📞", key("open")) ]]		

		return keyboard


	async def _act(self, order):
		self.keyboard = self.keyboard_()
		sent_message = await self.exec(Message(format_order(order, self.show)))
		
		#print(sent_message)
		#await remove_orders(self.context.dbbot, user_id=self.context.user.id, order_id=self.order.id)
		order_message = OrderMessage(
			user_id=self.context.message.chat_id,
			message_id=sent_message.message_id,
			order_id=order.id,
			#send_at=int(time.time())
		)
		self.context.dbbot.add(order_message)
		#self.keyboard = self.keyboard_()
		#return Message(format_order(order))
		if self.context.incomplete:
			self.context.get_message_id(sent_message.message_id)
		# print()
		# print(self.context.menu_stack)
		# print()
		self.register()
		return False

	async def handle_key_refresh(self):
		order = self.context.dbmain.query(Order_).filter(Order_.id==self.order_id).first()
		self.show = True if order.courier_id==self.context.courier.id else False
		self.keyboard = self.keyboard_()
		return Message(format_order(order))

	async def handle_key_status(self, status):
		if status not in status_.keys(): return "Xatolik yuzberdi"
		if status == 4:
			order = self.context.dbmain.query(Order_).filter(Order_.id==self.order_id).first()
			if not order: return "Xatolik yuzberdi"
			text = f"\n\nStatus ni {status_[status]} ga o'zgartirishni tasdiqlaysizmi?"
			self.keyboard = [[
				("Ha", key("confirm", status)),
				("Orqaga", key("refresh"))
			]]
			#return AmendMessage(text)
			return Message(format_order(order) + text)
		#await bot.answerCallbackQuery(query.id)
		# self.context.metadata['message_id']
		return await self.context.act(Comment, self.order_id, status)

	async def handle_key_confirm(self, status):
		if status not in status_.keys(): return "Xatolik yuzberdi"		
		result = await order_status(self.context.dbmain, self.context.courier, order_id=self.order_id, status=status)
		if not result: return "Xatolik yuzberdi"
		await remove_orders(self.context.dbbot, order_id=self.order_id)

	async def handle_key_open(self):
		courier = self.context.courier
		dbmain = self.context.dbmain
		opened_count = dbmain.query(Order_)\
			.filter(Order_.status==1, Order_.courier_id==courier.id).count()
		if opened_count>=courier.limet: return "Oldingi zakazlarni bitiring"
		
		order = dbmain.query(Order_).filter(Order_.id==self.order_id).first()
		if not order or order.status!=1: return "Xatolik yuzberdi"
		if order.courier_id!=None: return "Bu zakaz ochilgan uje"

		order.courier_id = courier.id

		order_view = OrderView(
			order_id=order.id,
			entity_type=1,
			entity_id=courier.id,
			date_time=datetime.datetime.now(),
		)
		dbmain.add(order_view)
		dbmain.commit()

		self.show = True
		self.keyboard = self.keyboard_()
		return Message(format_order(order, self.show))
		#await remove_orders(self.context.dbbot, order_id=order_id)

		#await bot.sendMessage(format_order(order), "-1001252819767")
		#return self.context.reset(Order, result)


class Comment(OutlineMenu):
	keyboard = [[ ("Orqaga", back()) ]]

	def _init(self, order_id, status):
		super()._init(order_id, status)
		self.order_id = order_id
		self.status = status
	
	async def _act(self, order_id, status):
		order = self.context.dbmain.query(Order_).filter(Order_.id==self.order_id).first()
		if not order: return "Xatolik yuzberdi"
		text = f"Status ni {status_[status]} ga o'zgartirmoqchisiz comment kiriting:"
		self.register()
		return Message(format_order(order) + text)

	async def handle_text(self, text):
		order_id, status = self.order_id, self.status
		tmp = await order_status(self.context.dbmain, self.context.courier, order_id=order_id, status=status, comment=text)
		if not tmp:
			await self.exec(Message("Xatolik yuzberdi"))
			return await self.context.back()

		await remove_orders(self.context.dbbot, order_id=order_id)
		await self.exec(Message("bajarildi"))
		return await self.context.back()


async def order_status(dbmain, courier,  order_id, status, comment=None):
	order = dbmain.query(Order_).filter(Order_.id==order_id).first()
	if not order or order.status!=1: return False
	offer = order.offer

	order.status = status
	order.courier_id = courier.id
	if comment:
		if not order.message: order.message = ''
		order.message += " \\\\ " + comment

	if status==4:
		courier.money += decimal.Decimal(float(order.cost) - courier.pay_for)
		product_store = dbmain.query(ProductStore).filter_by(
			product_id=offer.product_id,
			store_id=courier.store_id
		).first()
		if product_store:
			product_store.amount -= int(order.quantity)
		else:
			product_store = ProductStore(
				product_id=offer.product_id,
				store_id=courier.store_id,
				amount=-int(order.quantity)
			)
			dbmain.add(product_store)
			dbmain.commit()


	order_history = OrderHistory(order_id=order.id, courier_id=courier.id, changed_at=datetime.datetime.now(), status=status)
	dbmain.add(order_history)
	return True

	#await bot.sendMessage(format_order(order), status_channels[status])