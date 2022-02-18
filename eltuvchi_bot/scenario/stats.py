from photon import OutlineMenu, InlineMenu
from photon.objects import Message
import datetime
from dbsite import Order, OrderHistory
from sqlalchemy.sql import func

class WeeklyStats(OutlineMenu):
	async def _act(self):
		
		query = self.context.dbmain.execute('\n'.join([
			"SELECT",
				"DATE(orders_history.changed_at) AS 'date',",
				"SUM(IF(orders_history.status = 2, orders.quantity, NULL)) 'sold',",
				"COUNT(IF(orders_history.status = 3, 1, NULL)) 'recycled',",
				"COUNT(IF(orders_history.status = 4, 1, NULL)) 'delivered',",
				"COUNT(IF(orders_history.status = 5, 1, NULL)) 'cancelled',",
				"SUM(IF(orders_history.status in (2, 4), orders.cost, 0)) AS 'total'",
			"FROM orders_history",
			"LEFT JOIN orders ON orders_history.order_id=orders.id",
			"WHERE DATE(orders_history.changed_at)>DATE(NOW())-10 AND orders_history.courier_id=:courier_id",
			"GROUP BY date(orders_history.changed_at)"
		]), {"courier_id":self.context.courier.id})

		text = 'Kunlik ishlar bo\'yicha hissobot:\n'
		for tmp in query:
			sold = tmp.sold if tmp.sold else 0
			deliver_fee = self.context.courier.pay_for*tmp.delivered + 40000*sold
			text += '\n' + '\n'.join([
				f"🗓 {tmp.date}",
				f"💰 {tmp.total} | 🚚 {deliver_fee} | 💳 {int(tmp.total)-deliver_fee}",
				f"✅ {tmp.delivered} | ♻️ {tmp.recycled}",
			])

		return Message(text)


class DailyStats(OutlineMenu):
	async def _act(self):
		courier = self.context.courier
		total, i, j = 0, 0, 0
		text = 'Bugun siz yetkazgan buyurtmalar ro\'yxati:\n'
		delivery_cost = 0
		query = self.context.dbmain.query(OrderHistory, Order).filter(
			OrderHistory.courier_id==courier.id,
			OrderHistory.status.in_([2,4]),
			func.date(OrderHistory.changed_at)==datetime.date.today()
		).filter(Order.id==OrderHistory.order_id)

		for order_history, order in query:
			text += f"{i+1}|{order_history.changed_at.time()}|{order.cost}|{order.phone}\n"
			total += int(order.cost.replace(" ", ""))
			i, j = i+1, j+1
			if j>20:
				j = 0
				await self.exec(Message(text))
				text = ''

			if order_history.status==4:
				delivery_cost += courier.pay_for
			elif order_history.status==2:
				delivery_cost += 40000*order.quantity
				
		text += f'\n💰Jami savdo: {total}\n🚚Yo\'lkira:{delivery_cost}\n💳Kassa uchun:{total-delivery_cost}'

		return Message(text)