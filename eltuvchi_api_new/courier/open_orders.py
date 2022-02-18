

@register
async def PostOpenOrder(context, order_id:int):
	courier = context.courier
	db = context.db

	mine = db.query(Order).filter(and_(Order.status==1, Order.courier==courier.id)).count()
	if mine>=courier.limet: raise Exception("Oldingi zakazlarni bitiring")
	
	order = db.query(Order).filter(Order.id==order_id).first()
	if not order or order.status!=1: return False
	if order.courier!=None: raise Exception("Bu zakaz ochilgan uje")

	order.courier = courier.id

	order_view = OrderView(
		order_id=order.id,
		entity_type=1,
		entity_id=courier.id,
		date_time=datetime.datetime.now(),
	)
	db.add(order_view)
	db.commit()

	offer, cooperator = db.query(Offer, Cooperator).filter(Offer.id==order.offer_id).filter(Cooperator.id==order.operator).first()

	cooperator_name = cooperator.name if cooperator else None
	text = '\n'.join([
		f"👤 {order.name} 📱 {order.phone}",
		f"🛍 {order.quantity} dona {offer.short_name}, {order.cost} so'm",
		f"🏘 {order.region.name}, #{order.district.name}. {order.message}",
		f"🕥 {order.date_time}",
		f"👮 {cooperator_name} 🚚 {courier.name}",
	])

	await bot.sendMessage(text, "-1001252819767")
	return api.order(order, offer, cooperator)

@register
async def getOpenedOrders(context):
	result = []
	for order, offer, cooperator in context.db.query(Order, Offer, Cooperator)\
		.filter(Order.courier==courier.id, Order.status==1)\
		.filter(Offer.id==Order.offer_id)\
		.filter(Cooperator.id==Order.operator):
		result.append(api.order(order, offer, cooperator))
	return result