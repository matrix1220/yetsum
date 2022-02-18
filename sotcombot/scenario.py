from config import bot, db, language, statuses, filter_names
from dbscheme import User, OrderMessage
from object_dict import dictify, objectify
#from utilities import format

from photon.client import inline_button #bot
from photon import handler

from sqlalchemy import and_

import datetime
import asyncio
import re

session = db.session

def format_order_text(user, data):
	order, offer, cooperator = data
	if order.courier!=user.courier_id:
		order.phone = f"+998 *** {order.phone[-2:]}"
		order.secondary_phone = f"+998 *** {order.secondary_phone[-2:]}"
	order.region = filter_names[str(order.region_id)].name
	order.district = filter_names[str(order.region_id)].districts[str(order.district_id)].name
	order.date_time = str(datetime.datetime.fromtimestamp(order.date_time))
	cooperator = cooperator.name if cooperator else None
	text = language.order_message_text.format(order=order, offer=offer, cooperator=cooperator)
	return text

def format_order_keyboard(user, data):
	order, offer, cooperator = data
	if order.courier!=user.courier_id:
		keyboard = [[ inline_button("📞", [Order.Comment.id, order.id, 999]) ]]
	else:
		keyboard = [[ inline_button(y.symbol, [Order.Comment.id, order.id, x]) for x, y in statuses.items() ]]

	return keyboard


@handler
class MainMenu:
	async def act(user, arg=None):
		user.goback = []
		user.passes() 

		#await bot.sendMessage(user.id, language.welcome)
		keyboard = [
			[language.main.order, language.main.sold],
			[language.main.daily_stats, language.main.weekly_stats, language.main.balance]
		]
		return bot.sendMessage(user.id, language.main.message, keyboard=keyboard)

	async def handle_text(user, text):
		if text == "/help":
			return bot.sendMessage(user.id, language.help)
		elif text == language.main.order:
			return await user.explicit_act(Orders)()
		elif text == language.main.balance:
			courier = user.sotcom.get.me()
			text = f"Sizning qarzinggiz: {courier.money}"
			return bot.sendMessage(user.id, text)
		elif text == language.main.daily_stats:
			return await user.act(DailyStats)()
		elif text == language.main.weekly_stats:
			return await user.act(WeeklyStats)()
		elif text == language.main.sold:
			return await user.act(Sold)()
		else:
			match = re.match(r"^/id(\d*)$", text)
			if match:
				order_id = int(match.group(1))
				result = user.sotcom.get.Order(order_id=order_id)
				text = format_order_text(user, result)
				keyboard = format_order_keyboard(user, result)
				order_message = session.query(OrderMessage).filter(and_(
					OrderMessage.user_id==user.id,
					OrderMessage.order_id==order_id
				)).first()

				sent_message = await bot.sendMessage(user.id, text, inline_keyboard=keyboard)

				if order_message:
					try:
						await bot.deleteMessage(order_message.user_id, order_message.message_id)
					except:
						pass
					order_message.message_id = sent_message.message_id
				else:
					order_message = OrderMessage(user_id=user.id, message_id=sent_message.message_id, order_id=order_id)
					session.add(order_message)

			if reply_to := user.update.message.reply_to_message:
				order_message = session.query(OrderMessage).filter(and_(
					OrderMessage.user_id==user.id,
					OrderMessage.message_id==reply_to.message_id
				)).first()

				if not order_message:
					return bot.sendMessage(user.id, "Bu buyurtma emas.")

				result = user.sotcom.post.Comment(order_id=order_message.order_id, message=text)

				if not result:
					return bot.sendMessage(user.id, "Buyurtma serverda topilmadi")

				text = format_order_text(user, result)
				keyboard = format_order_keyboard(user, result)

				for order_message in session.query(OrderMessage).filter(OrderMessage.order_id==order_message.order_id):
					try:
						await bot.editMessageText(order_message.user_id, order_message.message_id, text, inline_keyboard=keyboard)
					except:
						pass


				return bot.sendMessage(user.id, "Bajarildi")

			return bot.sendMessage(user.id, "Qayta boshlash uchun /start bosing")

@handler
class WeeklyStats:
	async def act(user):
		text = 'Kunlik ishlar bo\'yicha hissobot:\n'
		for tmp in user.sotcom.get.WeeklyStats():
			sold = tmp.sold if tmp.sold else 0
			deliver_fee = tmp.courier_fee*tmp.delivered + 40000*sold
			text += '\n' + '\n'.join([
				f"🗓 {datetime.datetime.fromtimestamp(tmp.date).date()}",
				f"💰 {tmp.total} | 🚚 {deliver_fee} | 💳 {tmp.total-deliver_fee}",
				f"✅ {tmp.delivered} | ♻️ {tmp.recycled}",
			])

		return bot.sendMessage(user.id, text)


@handler
class Sold:
	async def act(user):
		user.passes()
		text = 'Tanlang:\n'
		keyboard = [[language.back]]
		user.menu_arguments = {"data":user.sotcom.get.Offers()}
		for tmp in user.menu_arguments.data:
			keyboard.append([tmp.short_name])

		return bot.sendMessage(user.id, text, keyboard=keyboard)

	async def handle_text(user, text):
		if text == language.back: return await user.back()
		for tmp in user.menu_arguments.data:
			if text==tmp.short_name:
				return await user.explicit_act(Sold.Count)(tmp.id)

		return bot.sendMessage(user.id, "topilmadi")

	@handler
	class Count:
		async def act(user, offer_id):
			user.passes()
			text = 'Nechta?\n'

			return bot.sendMessage(user.id, text, keyboard=[[language.back]])

		async def handle_text(user, text):
			if text == language.back: return await user.back()
			try:
				value = int(text)
			except Exception as e:
				return bot.sendMessage(user.id, "xato kritildi")

			return await user.explicit_act(Sold.Confirm)(user.current_menu()[1][0], value)

	@handler
	class Confirm:
		async def act(user, offer_id, count):
			user.passes()
			for tmp in user.menu_arguments.data:
				if offer_id==tmp.id:
					text = f"{tmp.price} so'mdan {count} dona {tmp.short_name} sotdingiz. Umumiy summa: {tmp.price*count} so'm. To'g'rimi?"
					return bot.sendMessage(user.id, text, keyboard=[[language.yeap, language.back]])

			await bot.sendMessage(user.id, "xatolik yuzberdi")
			return await user.back()

		async def handle_text(user, text):
			if text == language.back: return await user.back()
			elif text == language.yeap:
				tmp = user.sotcom.post.Order(offer_id=user.current_menu()[1][0], quantity=user.current_menu()[1][1])
				if tmp:
					await bot.sendMessage(user.id, "bajarildi")
				else:
					await bot.sendMessage(user.id, "xatolik yuzberdi")
			
			return await user.back()

@handler
class DailyStats:
	async def act(user):
		#user.passes()
		courier = user.sotcom.get.me()
		total, i, j = 0, 0, 0
		text = 'Bugun siz yetkazgan buyurtmalar ro\'yxati:\n'
		delivery_cost = 0
		for order_history, order in user.sotcom.get.DailyStats():
			text += f"{i+1}|{datetime.datetime.fromtimestamp(order_history.changed_at).time()}|{order.cost}|{order.phone}\n"
			total += int(order.cost.replace(" ", ""))
			i, j = i+1, j+1
			if j>20:
				j = 0
				await bot.sendMessage(user.id, text)
				text = ''

			if order_history.status==4:
				delivery_cost += courier.pay_for
			elif order_history.status==2:
				delivery_cost += 40000*order.quantity
				
		text += f'\n💰Jami savdo: {total}\n🚚Yo\'lkira:{delivery_cost}\n💳Kassa uchun:{total-delivery_cost}'

		return bot.sendMessage(user.id, text)

@handler
class Orders:
	async def act(user):
		user.filters = user.sotcom.get.Filters()
		keyboard = []
		keyboard.append([inline_button(f"Meniki ({user.filters.mine})", [Orders.Mine.id] )])

		for id, region in user.filters.regions.items():
			keyboard.append([inline_button(f"{region.name} ({region.count})", [Orders.Region.id, int(id)] )])
		for id, district in user.filters.districts.items():
			keyboard.append([inline_button(f"{district.name} ({district.count})", [Orders.District.id, int(id)] )])
		# if len(keyboard)==0:
		# 	return
		#keyboard.append([inline_button(language.all, [Orders.All.id] )])
		return bot.sendMessage(user.id, language.select, inline_keyboard=keyboard)
	
	@handler
	class Region:
		async def handle_callback(user, query, data):
			region_id, = data
			keyboard = []
			for id, district in user.filters.regions[str(region_id)].districts.items():
				keyboard.append([inline_button(f"{district.name} ({district.count})", [Orders.RegionDistrict.id, region_id, int(id)] )])
			#keyboard.append([inline_button(language.all, [Orders.WholeRegion.id, region_id] )])
			return bot.editMessageReplyMarkup(user.id, query.message.message_id, inline_keyboard=keyboard)
	
	@handler
	class Mine:
		async def handle_callback(user, query, data):
			await bot.deleteMessage(user.id, query.message.message_id)
			orders = user.sotcom.get.OpenedOrders()
			return await Orders.show(user, orders)

	@handler
	class All:
		async def handle_callback(user, query, data):
			await bot.deleteMessage(user.id, query.message.message_id)
			orders = user.sotcom.get.Orders()
			return await Orders.show(user, orders)
	
	@handler
	class District:
		async def handle_callback(user, query, data):
			await bot.deleteMessage(user.id, query.message.message_id)
			district_id, = data
			orders = user.sotcom.get.Orders(district_id=district_id)
			return await Orders.show(user, orders)

	@handler
	class WholeRegion:
		async def handle_callback(user, query, data):
			await bot.deleteMessage(user.id, query.message.message_id)
			region_id, = data
			orders = user.sotcom.get.Orders(region_id=region_id)
			return await Orders.show(user, orders)
	
	@handler
	class RegionDistrict:
		async def handle_callback(user, query, data):
			await bot.deleteMessage(user.id, query.message.message_id)
			region_id, district_id = data
			orders = user.sotcom.get.Orders(region_id=region_id, district_id=district_id)
			return await Orders.show(user, orders)

	async def show(user, orders):
		if orders==False or len(orders)==0:
			return bot.sendMessage(user.id, "Sizning so'rovingiz bo'yicha buyurtma topilmadi.")
		i = 0
		for data in orders:
			order, offer, cooperator = data
			text = format_order_text(user, data)
			keyboard = format_order_keyboard(user, data)
			i+=1
#			if i%10 == 0:
#			time.sleep(1)
			await asyncio.sleep(0.1)
			sent_message = await bot.queuedSendMessage(user.id, text, inline_keyboard=keyboard)
			order_message = session.query(OrderMessage).filter(and_(
				OrderMessage.user_id==user.id,
				OrderMessage.order_id==order.id
			)).first()
			if order_message:
				try:
					await bot.deleteMessage(user.id, order_message.message_id)
				except:
					pass
				order_message.message_id = sent_message.message_id
			else:
				order_message = OrderMessage(user_id=user.id, message_id=sent_message.message_id, order_id=order.id)
				session.add(order_message)


class Order:
	@handler
	class Show:
		async def handle_callback(user, query, data):
			order_id, = data
			result = user.sotcom.get.Order(order_id=order_id)
			text = format_order_text(user, result)
			keyboard = format_order_keyboard(user, result)
			order_message = session.query(OrderMessage).filter(and_(
				OrderMessage.user_id==user.id,
				OrderMessage.order_id==order_id
			)).first()

			# here might be bug
			if order_message:
				order_message.message_id = query.message.message_id
			else:
				order_message = OrderMessage(user_id=user.id, message_id=query.message.message_id, order_id=order_id)
				session.add(order_message)
			return bot.editMessageText(user.id, query.message.message_id, text, inline_keyboard=keyboard)
	
	@handler
	class Comment:
		async def act(user, order_id, status):
			user.passes()
			text = format_order_text(user, user.sotcom.get.Order(order_id=order_id))
			text += f"\n\nStatus ni {statuses[status].symbol} ga o'zgartirmoqchisiz comment kiriting:"
			message = await bot.sendMessage(user.id, text, keyboard=[[language.back]])
			user.menu_arguments = {"message_id":message.message_id}

		async def handle_callback(user, query, data):
			order_id, status = data
			if status==999: 
				try:
					result = user.sotcom.post.OpenOrder(order_id=order_id)
				except Exception as e:
					return bot.answerCallbackQuery(query.id, text=str(e))
				if not result: return bot.answerCallbackQuery(query.id, text=language.error)
				text = format_order_text(user, result)
				keyboard = format_order_keyboard(user, result)
				return bot.editMessageText(user.id, query.message.message_id, text, inline_keyboard=keyboard)
			if status not in statuses.keys(): return bot.answerCallbackQuery(query.id, text=language.error)
			if status == 4:
				text = query.message.text
				text += f"\n\nStatus ni {statuses[status].symbol} ga o'zgartirishni tasdiqlaysizmi?"
				keyboard = [[inline_button(language.yeap, [Order.Confirm.id, order_id, status]), inline_button(language.back, [Order.Show.id, order_id] )]]
				return bot.editMessageText(user.id, query.message.message_id, text, inline_keyboard=keyboard)
			await bot.answerCallbackQuery(query.id)
			return await user.act(Order.Comment)(order_id, status)

		async def handle_text(user, text):
			if text == language.back: return await user.back()
			order_id, status = user.current_menu()[1]
			tmp = user.sotcom.post.OrderStatus(order_id=order_id, status=status, message=text)
			if not tmp:
				await bot.sendMessage(user.id, "xatolik yuzberdi")
				return await user.back()

			for order_message in session.query(OrderMessage).filter(OrderMessage.order_id==order_id):
				try:
					await bot.deleteMessage(order_message.user_id, order_message.message_id)
				except:
					pass
				session.delete(order_message)

			await bot.deleteMessage(user.id, user.menu_arguments.message_id)
			await bot.sendMessage(user.id, "bajarildi")
			return await user.back()

	@handler
	class Confirm:
		async def handle_callback(user, query, data):
			order_id, status = data
			if status not in statuses.keys(): return bot.answerCallbackQuery(query.id, text=language.error)			
			data = user.sotcom.post.OrderStatus(order_id=order_id, status=status)
			if not data: return bot.answerCallbackQuery(query.id, text=language.error)
			for order_message in session.query(OrderMessage).filter(OrderMessage.order_id==order_id).all():
				try:
					await bot.deleteMessage(order_message.user_id, order_message.message_id)
				except:
					pass
				session.delete(order_message)
