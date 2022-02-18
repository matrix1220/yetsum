from dbscheme import Courier, Order, Cooperator, Offer, Districts, Regions, OrderHistory, Product
from dbscheme import OrderView, ProductStore
from dbscheme import row_as_dict
from utilities import escape, unescape
from config import db, bot, statuses
import time, decimal, datetime

from sqlalchemy import and_, or_
from sqlalchemy.sql import func


class getCourier:
	privileged_execute_arguments = {"telegram_id":int}
	def privileged_execute(session, data):
		courier = session.query(Courier).filter(Courier.telegram_id==data.telegram_id).first()
		if not courier: return False
		if courier.status!='1': return False
		return row_as_dict(courier)

class getOrders:
	#execute_arguments = {"region_id":int, "district_id":int}
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

	def execute(courier, data):
		filters = getOrders.get_filters(courier, data)
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

class getOrder:
	execute_arguments = {"order_id":int}
	def execute(courier, data):
		result = courier.session.query(Order, Offer, Cooperator).filter(Order.id==data.order_id)\
		.filter(Offer.id==Order.offer_id).filter(Cooperator.id==Order.operator).first()
		if not result: return False
		order, offer, cooperator = result
		return [row_as_dict(order), row_as_dict(offer), row_as_dict(cooperator)]

class getme:
	def execute(courier, data):
		return courier

class getFilters:
	def execute(courier, data):
		regions = {}

		if courier.regions:
			for region in courier.session.query(Regions).filter(Regions.id.in_(unescape(courier.regions))):
				districts = {}
				for district in region.districts:
					districts[district.id] = {
						"name":district.name,
						"count": courier.session.query(Order).filter(and_(
							Order.status==1, Order.district_id==district.id, Order.courier==None
						)).count()
					}
				regions[region.id] = {
					"name":region.name,
					"districts":districts,
					"count": courier.session.query(Order).filter(and_(
						Order.status==1, Order.region_id==region.id, Order.courier==None
					)).count()
				}

		districts = {}
		if courier.districts:
			for district in courier.session.query(Districts).filter(Districts.id.in_(unescape(courier.districts))):
				districts[district.id] = {
					"name":district.name,
					"count": courier.session.query(Order).filter(and_(
						Order.status==1, Order.district_id==district.id
					)).count()
				}
		mine = courier.session.query(Order).filter(and_(Order.status==1, Order.courier==courier.id)).count()
		return {"regions":regions, "districts":districts, "mine":f"{mine}/{courier.limet}" }

class getFilterNames:
	def privileged_execute(session, data):
		regions = {}
		for region in session.query(Regions):
			districts = {}
			for district in region.districts:
				districts[district.id] = {"name":district.name}
			regions[region.id] = {"name":region.name, "districts":districts}

		return regions

	def execute(courier, data):
		regions = {}
		if courier.regions:
			for region in courier.session.query(Regions).filter(Regions.id.in_(unescape(courier.regions))):
				districts = {}
				for district in region.districts:
					districts[district.id] = {"name":district.name}
				regions[region.id] = {"name":region.name, "districts":districts}

		if courier.districts:
			for district in courier.session.query(Districts).filter(Districts.id.in_(unescape(courier.districts))):
				if district.region_id not in regions:
					regions[district.region_id] = {"name":district.region.name, "districts":{district.id:{"name":district.name}}}

		return regions

class getOffers:
	def execute(courier, data):
		result = []
		# courier.session.query(ProductStore, Product) \
		# 	.filter(ProductStore.store_id==courier.store_id, ProductStore.amount>0) \
		# 	.join(Product, Product.id==ProductStore.product_id)
		for product in courier.session.query(Product).filter(getattr(Product, courier.store)>0):
			if not product.offer: continue
			result.append({"id":product.offer.id, "short_name":product.name, "price":product.offer.price})
		return result

class postOrder:
	execute_arguments = {"offer_id":int, "quantity":int}
	def execute(courier, data):
		offer = courier.session.query(Offer).filter(Offer.id==data.offer_id).first()
		if not offer: return False
		order = Order(
			user_id=0,
			date=datetime.datetime.now().date(),
			date_time=datetime.datetime.now(),
			phone='00000',
			ip=0,

			name=f"{courier.name} sotdi",
			offer_id=data.offer_id,
			courier=courier.id,
			quantity=data.quantity,
			cost=offer.price*data.quantity,
			status=2,
			paid=1
		)
		courier.session.add(order)
		courier.session.commit()

		courier.money += decimal.Decimal(float(order.cost) - data.quantity*40000)
		product_store = courier.session.query(ProductStore).filter_by(
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
			courier.session.add(product_store)
			courier.session.commit()


		order_history = OrderHistory(
			order_id=order.id,
			courier_id=courier.id,
			changed_at=datetime.datetime.now(),
			status=2
		)
		courier.session.add(order_history)

		text = '\n'.join([
			f"👤 {order.name}",
			#f"📱 {order.phone}",
			f"🛍 {order.quantity} dona {offer.short_name}, {order.cost} so'm",
			#f"🏘 {order.region.name}, #{order.district.name}. {order.message}",
		])
		#bot.sendMessage(statuses[4].channel, text)
		return True


class postOrderStatus:
	execute_arguments = {"order_id":int, "status":int}
	def execute(courier, data):
		order = courier.session.query(Order).filter(Order.id==data.order_id).first()
		if not order or order.status!=1: return False
		offer = courier.session.query(Offer).filter(Offer.id==order.offer_id).first()
		if not offer: return False


		order.status = data.status
		order.courier = courier.id
		if type(data.message)==str:
			if not order.message: order.message = ''
			order.message += " \\\\ " + data.message

		if data.status==4:
			courier.money += decimal.Decimal(float(order.cost) - courier.pay_for)
			product_store = courier.session.query(ProductStore).filter_by(
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
				courier.session.add(product_store)
				courier.session.commit()


		order_history = OrderHistory(order_id=order.id, courier_id=courier.id, changed_at=datetime.datetime.now(), status=data.status)
		courier.session.add(order_history)

		offer = courier.session.query(Offer).filter(Offer.id==order.offer_id).first()
		cooperator = courier.session.query(Cooperator).filter(Cooperator.id==order.operator).first()
		cooperator_name = cooperator.name if cooperator else None
		
		text = '\n'.join([
			f"👤 {order.name} 📱 {order.phone}",
			f"🛍 {order.quantity} dona {offer.short_name}, {order.cost} so'm",
			f"🏘 {order.region.name}, #{order.district.name}. {order.message}",
			f"🕥 {order.date_time}",
			f"👮 {cooperator_name} 🚚 {courier.name}",
		])
		#bot.sendMessage(statuses[data.status].channel, text)

		return True

class postComment:
	execute_arguments = {"order_id":int, "message":str}
	def execute(courier, data):
		order = courier.session.query(Order).filter(Order.id==data.order_id).first()
		if not order or order.status!=1: return False

		if not order.message: order.message = ''
		order.message += " | " + data.message

		offer, cooperator = courier.session.query(Offer, Cooperator).filter(Offer.id==order.offer_id).filter(Cooperator.id==order.operator).first()

		return [row_as_dict(order), row_as_dict(offer), row_as_dict(cooperator)]


class getWeeklyStats:
	def execute(courier, data):
		result = []
		tmp = courier.session.execute('\n'.join([
			"SELECT",
				"DATE(orders_history.changed_at) AS 'date',",
				"SUM(IF(orders_history.status = 2, orders.quantity, NULL)) 'sold',",
				"COUNT(IF(orders_history.status = 3, 1, NULL)) 'recycled',",
				"COUNT(IF(orders_history.status = 4, 1, NULL)) 'delivered',",
				"COUNT(IF(orders_history.status = 5, 1, NULL)) 'cancelled',",
				"SUM(IF(orders_history.status in (2, 4), orders.cost, 0)) AS 'total',",
				"couriers.pay_for AS 'courier_fee'",
			"FROM orders_history",
			"LEFT JOIN orders ON orders_history.order_id=orders.id",
			"INNER JOIN couriers ON orders_history.courier_id=couriers.id",
			"WHERE DATE(orders_history.changed_at)>DATE(NOW())-10 AND orders_history.courier_id=:courier_id",
			"GROUP BY date(orders_history.changed_at)"
		]), {"courier_id":courier.id})
		# orders_history.changed_at>DATE_SUB(CURRENT_DATE(), INTERVAL 10 DAY) AND
		for row in tmp:
			result.append(dict(row))

		return result

class getDailyStats:
	def execute(courier, data):
		return courier.session.query(OrderHistory, Order).filter(and_(
			OrderHistory.courier_id==courier.id,
			OrderHistory.status.in_([2,4]),
			func.date(OrderHistory.changed_at)==datetime.date.today()
		)).filter(Order.id==OrderHistory.order_id).all()

class postBackup:
	#sudo apt-get install mysql-client
	def privileged_execute(session, data):
		pass


class postOpenOrder:
	execute_arguments = {"order_id":int}
	def execute(courier, data):
		mine = courier.session.query(Order).filter(and_(Order.status==1, Order.courier==courier.id)).count()
		if mine>=courier.limet: raise Exception("Oldingi zakazlarni bitiring")
		
		order = courier.session.query(Order).filter(Order.id==data.order_id).first()
		if not order or order.status!=1: return False
		if order.courier!=None: raise Exception("Bu zakaz ochilgan uje")

		order.courier = courier.id

		order_view = OrderView(
			order_id=123,
			entity_type=1,
			entity_id=courier.id,
			date_time=datetime.datetime.now(),
		)
		courier.session.add(order_view)
		courier.session.commit()

		offer, cooperator = courier.session.query(Offer, Cooperator).filter(Offer.id==order.offer_id).filter(Cooperator.id==order.operator).first()

		cooperator_name = cooperator.name if cooperator else None
		text = '\n'.join([
			f"👤 {order.name} 📱 {order.phone}",
			f"🛍 {order.quantity} dona {offer.short_name}, {order.cost} so'm",
			f"🏘 {order.region.name}, #{order.district.name}. {order.message}",
			f"🕥 {order.date_time}",
			f"👮 {cooperator_name} 🚚 {courier.name}",
		])

		#bot.sendMessage("-1001252819767", text)
		return [row_as_dict(order), row_as_dict(offer), row_as_dict(cooperator)]

class getOpenedOrders:
	def execute(courier, data):
		result = []
		for order, offer, cooperator in courier.session.query(Order, Offer, Cooperator)\
			.filter(Order.courier==courier.id, Order.status==1)\
			.filter(Offer.id==Order.offer_id)\
			.filter(Cooperator.id==Order.operator):
			result.append([row_as_dict(order), row_as_dict(offer), row_as_dict(cooperator)])
		return result