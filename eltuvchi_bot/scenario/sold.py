
from photon import key, act, explicit_act, reset, back
from photon import OutlineMenu, InlineMenu
from photon.objects import Message
from dbsite import ProductStore, Product, Offer, Order, OrderHistory
import datetime, decimal

class Sold(OutlineMenu):
	
	async def _act(self):
		self.keyboard = [[ ("Orqaga", back()) ]]

		for product_store in self.context.dbmain.query(ProductStore) \
			.filter(ProductStore.store_id==self.context.courier.store_id, ProductStore.amount>0):
			for offer in product_store.product.offers:
				self.keyboard.append([(offer.short_name, key("select", offer.id))])

		self.register()
		return Message('Tanlang:\n')

	async def handle_key_select(self, offer_id):
		return await self.context.explicit_act(SoldCount, offer_id)

	# async def handle_text(user, text):
	# 	offer = self.context.dbmain.query(Offer).filter(Offer.short_name==text).first()
	# 	return await self.context.explicit_act(Count, offer.id)

	# 	return Message("topilmadi")

	
class SoldCount(OutlineMenu):
	keyboard = [[ ("Orqaga", back()) ]]
	def _init(self, offer_id):
		super()._init(offer_id)
		self.offer_id = offer_id

	async def _act(self, offer_id):
		self.register()
		return Message('Nechta?')

	async def handle_text(self, text):
		try:
			value = int(text)
		except Exception as e:
			return Message("xato kritildi")

		return await self.context.explicit_act(SoldConfirm, self.offer_id, value)


class SoldConfirm(OutlineMenu):
	def _init(self, offer_id, count):
		super()._init(offer_id, count)
		self.offer_id = offer_id
		self.count = count

	async def _act(self, offer_id, count):
		offer = self.context.dbmain.query(Offer).filter(Offer.id==offer_id).first()
		if not offer:
			await self.exec(Message("xatolik yuzberdi"))
			return await self.context.back()

		text = f"{offer.price} so'mdan {self.count} dona {offer.short_name} sotdingiz. Umumiy summa: {offer.price*self.count} so'm. To'g'rimi?"
		self.keyboard=[[("Ha", key("yeap")), ("Orqaga", back())]]
		self.register()
		return Message(text)
		
		return await self.context.back()

	async def handle_key_yeap(self):
		courier = self.context.courier
		dbmain = self.context.dbmain
		offer = dbmain.query(Offer).filter(Offer.id==self.offer_id).first()
		order = Order(
			date=datetime.datetime.now().date(),
			date_time=datetime.datetime.now(),
			name=f"{courier.name} sotdi",
			offer_id=self.offer_id,
			courier_id=courier.id,
			quantity=self.count,
			cost=str(offer.price*self.count),
			status=2,
			paid=1,
			user_id=0,
			phone='00000',
			ip=0,
		)
		dbmain.add(order)
		dbmain.commit()

		courier.money += decimal.Decimal(float(order.cost) - order.quantity*40000)
		product_store = dbmain.query(ProductStore).filter_by(
			product_id=offer.product_id,
			store_id=courier.store_id
		).first()
		if product_store:
			product_store.amount -= order.quantity
		else:
			product_store = ProductStore(
				product_id=offer.product_id,
				store_id=courier.store_id,
				amount=-order.quantity
			)
			dbmain.add(product_store)
			dbmain.commit()


		order_history = OrderHistory(
			order_id=order.id,
			courier_id=courier.id,
			changed_at=datetime.datetime.now(),
			status=2
		)
		dbmain.add(order_history)

		# text = '\n'.join([
		# 	"test",
		# 	f"👤 {order.name}",
		# 	f"🛍 {order.quantity} dona {offer.short_name}, {order.cost} so'm",
		# ])
		# await bot.sendMessage(text, status_channel[4])
		await self.exec(Message("bajarildi"))
		return await self.context.back()

	# async def handle_text(self, text):
	# 	return await self.context.back()