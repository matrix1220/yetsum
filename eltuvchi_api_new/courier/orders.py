
def get_filters(courier, data):
	regions = unescape(courier.regions) if courier.regions else []
	districts = unescape(courier.districts) if courier.districts else []

	if data.district_id:
		if data.district_id in districts:
			return Order.district_id==data.district_id
		elif data.region_id:
			#district = courier.session.query(Districts).filter(Districts.id==data.district_id).first()
			return and_(Order.region_id==data.region_id, Order.district_id==data.district_id)

	elif data.region_id and data.region_id in regions:
		return Order.region_id==data.region_id
	else:
		return or_(Order.region_id.in_(regions), Order.district_id.in_(districts))

	return False

async def GetOrders(context):
	filters = get_filters(courier, data)
	if filters==False: return False

	result = [] # , getattr(Order.offer.product, courier.store)>0 
	for order, offer, cooperator in courier.session.query(Order, Offer, Cooperator)\
		.filter(and_(filters, or_(
			Order.courier==None,
			Order.courier==courier.id
		), Order.status==1))\
		.filter(Offer.id==Order.offer_id)\
		.filter(Cooperator.id==Order.operator):
		result.append([row_as_dict(order), row_as_dict(offer), row_as_dict(cooperator)])
	return result
		