

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