from config import bot
from photon.utils import format
from photon import MenuHandler, CallbackHandler
from photon.methods import sendMessage
from dbbot import Ad, AdType, session

import dbsite
from dbsite import Stream, User


class MainMenu(MenuHandler):
	async def act(user, arg=None):
		#if user.language==None: return user.act(SelectLanguage)()
		user.passes()
		if arg:
			return await user.act(ShowAd)(arg)
		else:
			usr = dbsite.session.query(User).filter(User.telegram_id==user.id).first()
			if usr:
				user.user_id = usr.id
				keyboard = [['Balans']]
				return bot.sendMessage(user.id, 'Bosh menu', keyboard=keyboard)

	async def handle_text(user, text):
		if user.id in [181040037, 108268232]:
			if text == "/add_ad":
				return await user.act(AddAd)()
			elif text == "/delete_ad":
				return await user.act(DeleteAd)()

		if user.user_id:
			usr = dbsite.session.query(User).filter(User.id==user.user_id).first()
			if usr:
				if text == "Balans":
					return bot.sendMessage(user.id, f"{usr.money}")

	async def handle_message(user, message):
		pass

class ShowAd(MenuHandler):
	async def act(user, url):
		stream = dbsite.sesstion.query(Stream).filter(Stream.url==url).first()
		if not stream: return sendMessage(user.id, "oqim topilmadi")

		for ad in session.query(Ad).filter(Ad.offer_id==stream.offer_id):
			caption = ad.caption.format(stream=stream)
			if ad.type==AdType.text:
				await sendMessage(user.id, caption, remove_keyboard=True)
			if ad.type==AdType.video:
				await bot.sendVideo(user.id, ad.data, caption=caption, remove_keyboard=True)
		# user.menu_arguments = {"url":url}
		# keyboard = []
		# for ad in session.query(Ad).filter(Ad.offer_id==stream.offer_id):
		# 	keyboard.append([f"{ad.id}: {ad.name}"])

		# if len(keyboard)==0:
		# 	return sendMessage(user.id, "reklama topilmadi")

		# user.passes()
		# return bot.sendMessage(user.id, 'tanlang:', keyboard=keyboard)

	async def handle_text(user, text):
		# stream = dbsite.sesstion.query(Stream).filter(Stream.url==user.menu_arguments.url).first()
		# for ad in session.query(Ad).filter(Ad.offer_id==stream.offer_id):
		# 	if text==f"{ad.id}: {ad.name}":
		# 		caption = ad.caption.format(stream=stream)
		# 		if ad.type==AdType.text:
		# 			await sendMessage(user.id, caption, remove_keyboard=True)
		# 		if ad.type==AdType.video:
		# 			await bot.sendVideo(user.id, ad.data, caption=caption, remove_keyboard=True)

		return await user.act(MainMenu)()


class DeleteAd(MenuHandler):
	async def act(user):
		user.passes()
		keyboard = []
		for ad in session.query(Ad):
			keyboard.append([f"{ad.id}: {ad.name}"])
		return bot.sendMessage(user.id, 'tanlang:', keyboard=keyboard)

	async def handle_text(user, text):
		for ad in session.query(Ad):
			if text==f"{ad.id}: {ad.name}":
				session.delete(ad)
				await bot.sendMessage(user.id, 'done', remove_keyboard=True)

		return await user.act(MainMenu)()

class AddAd(MenuHandler):
	async def act(user):
		return await user.act(AddAd.OfferId)()

	class OfferId(MenuHandler):
		async def act(user):
			user.passes()
			return bot.sendMessage(user.id, 'input offer_id')
		async def handle_text(user, text):
			user.menu_arguments = {"offer_id":int(text)}
			return await user.act(AddAd.Name)()

		async def handle_message(user, message):
			pass

	class Name(MenuHandler):
		async def act(user):
			user.passes()
			return bot.sendMessage(user.id, 'input name')
		async def handle_text(user, text):
			user.menu_arguments.name = text
			return await user.act(AddAd.Data)()

		async def handle_message(user, message):
			pass

	class Data(MenuHandler):
		async def act(user):
			user.passes()
			return bot.sendMessage(user.id, 'input data')

		async def handle_text(user, text):
			user.menu_arguments.caption = text
			ad = Ad(offer_id=user.menu_arguments.offer_id, name=user.menu_arguments.name, type=AdType.text, caption=user.menu_arguments.caption)
			session.add(ad)
			return await user.act(MainMenu)()

		async def handle_video(user, video):
			pass

		async def handle_message(user, message):
			if video:=message.video:
				ad = Ad(offer_id=user.menu_arguments.offer_id, name=user.menu_arguments.name, type=AdType.video, caption=message.caption, data=video.file_id)
				session.add(ad)
				await bot.sendMessage(user.id, 'done')
				return await user.act(MainMenu)()
