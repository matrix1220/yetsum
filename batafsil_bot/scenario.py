from config import bot#, languages
from photon.utils import format
from photon import MenuHandler, CallbackHandler
from photon.methods import sendMessage
import dbbot, dbsite
session = dbbot.session
#from dbbot import Ad, AdType
from dbsite import Stream, Order, Offer

import re, datetime


class MainMenu(MenuHandler):
	async def act(user, arg=None):
		#if user.language==None: return user.act(SelectLanguage)()
		user.passes()
		if not arg: return sendMessage(user.id, "Botni faqat maxsus taklif ssilkasi orqali ishlatish mumkin")
		return await user.act(RegisterOrder)(arg)
		#keyboard = [['/add_ad']]
		#return bot.sendMessage(user.id, 'salom', keyboard=keyboard)

	async def handle_text(user, text):
		pass

	async def handle_message(user, message):
		pass

class RegisterComplete(MenuHandler):
	async def act(user):
		user.passes()

	async def handle_text(user, text):
		pass

	async def handle_message(user, message):
		pass

class RegisterOrder(MenuHandler):
	async def act(user, url):
		stream = dbsite.session.query(Stream).filter(Stream.url==url).first()
		if not stream: return sendMessage(user.id, "oqim topilmadi")
		user.menu_arguments = {
			"offer_id": stream.offer_id,
			"stream_id": stream.id,
			"user_id": stream.user_id,
			"template_id": stream.template_id
		}
		offer = dbsite.session.query(Offer).filter(Offer.id==user.menu_arguments.offer_id).first()
		if not offer: return sendMessage(user.id, "offer topilmadi")

		user.passes()
		await bot.sendMessage(user.id, f"*{offer.name}*\n\n{offer.small_descr}\n\n💰 Narxi: {offer.price} so'm\nButun O'zbekiston bo'ylab yekazib berish xizmati mavjud", parse_mode="Markdown")
		return sendMessage(user.id, "Batafsil ma'lumot uchun raqamingizni yuboring, operator siz bilan aloqacha chiqadi", keyboard=[[{"text":"Raqamni yuborish", "request_contact":True}]])

	async def handle_text(user, text):
		pass

	async def handle_message(user, message):
		phone = None
		if contact:=message.contact:
			phone = contact.phone_number
			name = contact.first_name
		if text:=message.text:
			phone = text
			name = message['from'].first_name

		if not phone: return sendMessage(user.id, "qabul qilib bo'lmaydigan malumot")

		match = re.match(r"(\+?998)?(?P<phone>\d{9})$", phone)
		#print(match)
		if match==None: return sendMessage(user.id, 'xato kiritdinggiz')
		phone = match.group('phone')
		offer = dbsite.session.query(Offer).filter(Offer.id==user.menu_arguments.offer_id).first()
		order = Order(
			offer_id=user.menu_arguments.offer_id,
			stream_id=user.menu_arguments.stream_id,
			user_id=user.menu_arguments.user_id,
			template_id=user.menu_arguments.template_id,
			name=name,
			phone=phone,
			paid=0,
			status=0,
			date_time=datetime.datetime.now(),
			date=datetime.datetime.now().date(),
			quantity=1,
			money=offer.pay_for,
			cost=offer.price,
			ip=0
		)
		dbsite.session.add(order)
		dbsite.session.commit()
		user.menu_arguments.order_id = order.id
		await sendMessage(-1001471477939, f"👤 {name}\n♻️ {offer.short_name}\n📱 {phone}\n🆔 {order.id} {order.user_id}")

		await sendMessage(user.id, f"Buyurtma qabul qilindi")
		return await user.act(RegisterComplete)()