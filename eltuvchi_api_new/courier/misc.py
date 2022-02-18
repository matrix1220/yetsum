

# class getOffers:
# 	def execute(courier, data):
# 		result = []
# 		# courier.session.query(ProductStore, Product) \
# 		# 	.filter(ProductStore.store_id==courier.store_id, ProductStore.amount>0) \
# 		# 	.join(Product, Product.id==ProductStore.product_id)
# 		for product in courier.session.query(Product).filter(getattr(Product, courier.store)>0):
# 			if not product.offer: continue
# 			result.append({"id":product.offer.id, "short_name":product.name, "price":product.offer.price})
# 		return result

# @register
# async def GetMe(context):
# 	return context.courier


class postComment:
	execute_arguments = {"order_id":int, "message":str}
	def execute(courier, data):
		order = courier.session.query(Order).filter(Order.id==data.order_id).first()
		if not order or order.status!=1: return False

		if not order.message: order.message = ''
		order.message += " | " + data.message

		offer, cooperator = courier.session.query(Offer, Cooperator).filter(Offer.id==order.offer_id).filter(Cooperator.id==order.operator).first()

		return [row_as_dict(order), row_as_dict(offer), row_as_dict(cooperator)]