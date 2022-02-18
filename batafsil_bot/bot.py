from config import bot
import dbbot, dbsite
import photon, scenario

async def handle(update):
	_response = await photon.handle(update)

	try:
		dbsite.session.commit()
	except:
		dbsite.session.rollback()
		raise

	try:
		dbbot.session.commit()
	except:
		dbbot.session.rollback()
		raise
		
	# dbbot.session.commit()
	# try:
	# 	_response = await photon.handle(update) # photon.handle
	# finally:
	# 	dbbot.session.commit()
	# 	dbsite.session.commit()
	# 	# try:
	# 	# 	dbbot.session.commit()
	# 	# 	dbsite.session.commit()
	# 	# except:
	# 	# 	session.rollback()
	# 	# 	raise
	return _response