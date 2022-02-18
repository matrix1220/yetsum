from . import register

@register
async def GetMe(context):
	return "hello"

@register
async def GetOrder(context, order_id: int):
	result = context.db.query(Order, Offer, Cooperator).filter(Order.id==order_id)\
	.filter(Offer.id==Order.offer_id).filter(Cooperator.id==Order.operator).first()
	if not result: return False
	order, offer, cooperator = result
	return [row_as_dict(order), row_as_dict(offer), row_as_dict(cooperator)]




# class postOrder:
# 	execute_arguments = {"offer_id":int, "quantity":int}
# 	def execute(courier, data):
# 		offer = courier.session.query(Offer).filter(Offer.id==data.offer_id).first()
# 		if not offer: return False
# 		order = Order(
# 			user_id=0,
# 			date=datetime.datetime.now().date(),
# 			date_time=datetime.datetime.now(),
# 			phone='00000',
# 			ip=0,

# 			name=f"{courier.name} sotdi",
# 			offer_id=data.offer_id,
# 			courier=courier.id,
# 			quantity=data.quantity,
# 			cost=offer.price*data.quantity,
# 			status=2,
# 			paid=1
# 		)
# 		courier.session.add(order)
# 		courier.session.commit()

# 		courier.money += decimal.Decimal(float(order.cost) - data.quantity*40000)
# 		product_store = courier.session.query(ProductStore).filter_by(
# 			product_id=offer.product_id,
# 			store_id=courier.store_id
# 		).first()
# 		if product_store:
# 			product_store.amount -= int(order.quantity)
# 		else:
# 			product_store = ProductStore(
# 				product_id=offer.product_id,
# 				store_id=courier.store_id,
# 				amount=-int(order.quantity)
# 			)
# 			courier.session.add(product_store)
# 			courier.session.commit()


# 		order_history = OrderHistory(
# 			order_id=order.id,
# 			courier_id=courier.id,
# 			changed_at=datetime.datetime.now(),
# 			status=2
# 		)
# 		courier.session.add(order_history)

# 		text = '\n'.join([
# 			f"👤 {order.name}",
# 			#f"📱 {order.phone}",
# 			f"🛍 {order.quantity} dona {offer.short_name}, {order.cost} so'm",
# 			#f"🏘 {order.region.name}, #{order.district.name}. {order.message}",
# 		])
# 		bot.sendMessage(statuses[4].channel, text)
# 		return True


# class postOrderStatus:
# 	execute_arguments = {"order_id":int, "status":int}
# 	def execute(courier, data):
# 		order = courier.session.query(Order).filter(Order.id==data.order_id).first()
# 		if not order or order.status!=1: return False
# 		offer = courier.session.query(Offer).filter(Offer.id==order.offer_id).first()
# 		if not offer: return False


# 		order.status = data.status
# 		order.courier = courier.id
# 		if type(data.message)==str:
# 			if not order.message: order.message = ''
# 			order.message += " \\\\ " + data.message

# 		if data.status==4:
# 			courier.money += decimal.Decimal(float(order.cost) - courier.pay_for)
# 			product_store = courier.session.query(ProductStore).filter_by(
# 				product_id=offer.product_id,
# 				store_id=courier.store_id
# 			).first()
# 			if product_store:
# 				product_store.amount -= int(order.quantity)
# 			else:
# 				product_store = ProductStore(
# 					product_id=offer.product_id,
# 					store_id=courier.store_id,
# 					amount=-int(order.quantity)
# 				)
# 				courier.session.add(product_store)
# 				courier.session.commit()


# 		order_history = OrderHistory(order_id=order.id, courier_id=courier.id, changed_at=datetime.datetime.now(), status=data.status)
# 		courier.session.add(order_history)

# 		offer = courier.session.query(Offer).filter(Offer.id==order.offer_id).first()
# 		cooperator = courier.session.query(Cooperator).filter(Cooperator.id==order.operator).first()
# 		cooperator_name = cooperator.name if cooperator else None
		
# 		text = '\n'.join([
# 			f"👤 {order.name} 📱 {order.phone}",
# 			f"🛍 {order.quantity} dona {offer.short_name}, {order.cost} so'm",
# 			f"🏘 {order.region.name}, #{order.district.name}. {order.message}",
# 			f"🕥 {order.date_time}",
# 			f"👮 {cooperator_name} 🚚 {courier.name}",
# 		])
# 		bot.sendMessage(statuses[data.status].channel, text)

# 		return True



