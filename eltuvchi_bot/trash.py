

courier = dbsite.session.query(Couriers).filter(and_(Couriers.telegram_id==chat.id, Couriers.status=='1')).first()
if courier is not None:
	for order, offer in dbsite.session.query(Orders, Offers).filter(and_(Orders.region==courier.region, Orders.status==1)).filter(Offers.id==Orders.offer_id):
		text = f"👤 {order.name}\n♻️ {order.quantity} dona {offer.short_name}💰 {order.cost}\n📱 {order.phone}\n🏘 {order.region}\n📌 {order.message}"
		bot.sendMessage(chat.id, text)


elif text == "/update_orders" and user.courier_id:
	active_orders = sotcom.get.ActiveOrders(region=user.region)
	for order_message in db.session.query(OrderMessage).all():
		found = False
		for x, pack in enumerate(active_orders):
			order, offer = pack
			if order.id == order_message.order_id:
				found = True
				del active_orders[x]
				break
		if not found:
			bot.deleteMessage(chat.id, order_message.message_id)

	for order, offer in active_orders:
		text = language.order_message_text.format(order=order, offer=offer)
		keyboard = format(language.order_message_keyboard, order=order)
		sent_message = bot.sendMessage(chat.id, text, reply_markup={"inline_keyboard":keyboard})
		order_message = db.session.query(OrderMessage).filter(OrderMessage.order_id==order.id).first()
		if order_message:
			order_message.message_id = sent_message.message_id
		else:
			order_message = OrderMessage(user_id=user.id, message_id=sent_message.message_id, order_id=order.id)
			db.session.add(order_message)




def checkCourier(user):
	courier = sotcom.get.ActiveCourier(telegram_id=user.id)
	user.last_check = time.time()
	if courier:
		user.courier_id = courier.id
		user.region = courier.region
		return True
	else:
		user.courier_id = 0
		user.region = None
		user.menu = None
		for order_message in db.session.query(OrderMessage).filter(OrderMessage.user_id==user.id).all():
			try:
				bot.deleteMessage(order_message.user_id, order_message.message_id)
			except:
				pass
			db.session.delete(order_message)
		return False


	try:
		response = main(update)
		db.session.commit()
		return response
	except Exception as e:
		import traceback
		print(traceback.format_exc(), str(e))
		bot.sendMessage(-1001175870627, traceback.format_exc() + "\n\n" + str(e))


	elif matches := re.match(r"/clear (?P<id>\d+)", text):
		if user.id not in [181040037, 108268232]: return
		victim = findUser(matches.group('id'))
		checkCourier(victim)
		return response.sendMessage(user.id, "done")



	elif text == language.main.balance:
		courier = sotcom.get.ActiveCourier(telegram_id=user.id)
		return response.sendMessage(user.id, f"💸 Sizning qarzingiz: {courier.money}")
	elif text == language.main.daily_stats:
		courier = sotcom.get.ActiveCourier(telegram_id=user.id)
		total = 0
		text = 'Bugun siz yetkazgan buyurtmalar ro\'yxati:\n'
		i, j = 0, 0
		for order_history, order in sotcom.get.DailyStats(courier_id=user.courier_id):
			text += str(i+1) + '|' + \
				str(datetime.datetime.strptime(order_history.changed_at, '%Y-%m-%d %H:%M:%S').time()) + '|' +\
				str(order.cost) + '|' +\
				str(order.phone) + '\n'
			total += int(order.cost)
			i+=1
			j+=1
			if j>20:
				j = 0
				bot.sendMessage(user.id, text)
				text = ''

		pay_for = i * int(courier.pay_for)
		text += f'\n💰Jami savdo: {total}\n🚚Yo\'lkira:{pay_for}\n💳Kassa uchun:{total-pay_for}'

		return response.sendMessage(user.id, text)
	elif text == language.main.weekly_stats:
		text = 'Kunlik ishlar bo\'yicha hissobot:\n\n'
		for record in sotcom.get.WeeklyStats(courier_id=user.courier_id):
			fee = int(record.c4)*int(record.fee)
			text += f"🗓{record.date}\n💰{record.total} | 🚚 {fee} | 💳 {int(record.total)-fee}\n✅{record.c4} | ♻️{record.c3} | ❌{record.c5} \n\n"

		return response.sendMessage(user.id, text)



		if command == 1:
			order_id, status = data
			if status not in channels.keys(): return response.answerCallbackQuery(callback_query.id, text=language.error)

			order, offer, cooperator = sotcom.get.ActiveOrder(order_id=order_id)
			status_emoji = {3:"♻️", 4:"✅", 5:"❌"}[status]
			text = language.order_message_text.format(order=order, offer=offer, cooperator=cooperator.name if cooperator else None)
			text += f"\n\nStatus ni {status_emoji} ga o'zgartirishni tasdiqlaysizmi?"
			keyboard = [[inline_button("Ha", escape(4, order_id, status)), inline_button(language.back, escape(5, order_id))]]
			return response.editMessageText(user.id, callback_query.message.message_id, text=text, inline_keyboard=keyboard)
		elif command == 5:
			order_id, = data
			order, offer, cooperator = sotcom.get.ActiveOrder(order_id=order_id)
			text = language.order_message_text.format(order=order, offer=offer, cooperator=cooperator.name if cooperator else None)
			keyboard = format(language.order_message_keyboard, order=order)
			message = callback_query.message
			order_message = db.session.query(OrderMessage).filter(and_(OrderMessage.user_id==user.id, OrderMessage.order_id==order.id)).first()
			if order_message:
				order_message.message_id = message.message_id
			else:
				order_message = OrderMessage(user_id=user.id, message_id=message.message_id, order_id=order.id)
				db.session.add(order_message)
			return response.editMessageText(user.id, message.message_id, text=text, inline_keyboard=keyboard)
		elif command == 4:
			order_id, status = data
			if status not in channels.keys(): return response.answerCallbackQuery(callback_query.id, text=language.error)			
			data = sotcom.post.OrderStatus(courier_id=user.courier_id, order_id=order_id, status=status)
			if data: 
				order, offer, cooperator = data
				text = language.order_message_text.format(order=order, offer=offer, cooperator=cooperator.name if cooperator else None)
				for order_message in db.session.query(OrderMessage).filter(OrderMessage.order_id==order.id).all():
					try:
						bot.deleteMessage(order_message.user_id, order_message.message_id)
					except:
						pass
					db.session.delete(order_message)
				bot.sendMessage(channels[status], text)
				#return response.deleteMessage(user.id, callback_query.message.message_id)
			else:
				return response.answerCallbackQuery(callback_query.id, text=language.error)
		elif command == 2:
			district, = data
			bot.editMessageText(user.id, callback_query.message.message_id, text='Tuman: ' + district)
			for order, offer, cooperator in sotcom.get.ActiveOrders(region=user.region, district=district):
				text = language.order_message_text.format(order=order, offer=offer, cooperator=cooperator.name if cooperator else None)
				keyboard = format(language.order_message_keyboard, order=order)
				sent_message = bot.sendMessage(user.id, text, inline_keyboard=keyboard)
				order_message = db.session.query(OrderMessage).filter(and_(OrderMessage.user_id==user.id, OrderMessage.order_id==order.id)).first()
				if order_message:
					try:
						bot.deleteMessage(user.id, order_message.message_id)
					except:
						pass
					order_message.message_id = sent_message.message_id
				else:
					order_message = OrderMessage(user_id=user.id, message_id=sent_message.message_id, order_id=order.id)
					db.session.add(order_message)
		elif command == 3:
			subcommand = data.pop(0)
			if subcommand == 0:
				pass
			elif subcommand == 1:
				pass

			return response.answerCallbackQuery(callback_query.id, text="not implemented")