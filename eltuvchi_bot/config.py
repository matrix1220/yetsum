
import os.path
debug = os.path.exists("debug")

import logging
if debug:
	logging.basicConfig(level=logging.DEBUG)
	logging.getLogger('hpack').setLevel(logging.ERROR)
	
else:
	logging.basicConfig(filename='app.log', filemode='w', level=logging.ERROR)


# import dbscheme
# db.base.metadata.create_all(db.engine)

import yaml
from object_dict import objectify

status_ = {4:"✅", 3:"♻️"}
status_channel = {4:-1001476356831, 3:-1001285547213}

# with open('least_handlers_time', 'r') as reader:
# 	least_handlers_time = int(reader.read())

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

bot_database_engine = create_engine('sqlite:///datebase.db')
bot_session_maker = sessionmaker(bind=bot_database_engine)

if debug:
	main_database_engine = create_engine('mysql+mysqlconnector://root:default@localhost/sotcom')
else:
	main_database_engine = create_engine('mysql+mysqlconnector://sotuvchi_api:123456@10.0.0.4/sotuvchi_new')
main_session_maker = sessionmaker(bind=main_database_engine)

# 359269508:AAE5TKgX3f2VC5gNxaUztSTxThswsRr_BIk
# 287925905:AAEsaBOKVGoKDiGxBr1aaBxkpYn4AHUpbJQ dev botmoq
# 305643264:AAGwALg3QDiH2OrNzqehgoPdeXwpIqY416c dev aybir
# 1439060825:AAGp1-jD1KunOffsw2d-xP1npEkIxg_PMww prod
if debug:
	_token = "287925905:AAEsaBOKVGoKDiGxBr1aaBxkpYn4AHUpbJQ"
else:
	_token = "1439060825:AAGp1-jD1KunOffsw2d-xP1npEkIxg_PMww"


from photon import Bot
from context import ContextManager
bot = Bot(_token, context_manager=ContextManager())