import os.path
debug = os.path.exists("debug")

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker as _sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import logging
if debug:
	logging.basicConfig(level=logging.DEBUG)
else:
	logging.basicConfig(filename='app.log', filemode='w', level=logging.ERROR)

class db:
	base = declarative_base()
	
	if debug:
		engine = create_engine('mysql+mysqlconnector://matrix1220@localhost/sotcom')
	else:
		engine = create_engine('mysql+mysqlconnector://sotuvchi_api:123456@10.0.0.4/sotuvchi_new')
		
	#engine = create_engine(f"mysql+mysqlconnector://sotuvchi_api:123456@127.0.0.1:{server.local_bind_port}/sotuvchi_new", echo=True)
	sessionmaker = _sessionmaker(bind=engine)
	#session = sessionmaker()

import Telegrambot
bot = Telegrambot.bot("1439060825:AAGp1-jD1KunOffsw2d-xP1npEkIxg_PMww")

from object_dict import objectify
statuses = objectify({4:{"channel":-1001476356831, "symbol":"✅"}, 3:{"channel":-1001285547213, "symbol":"♻️"}})

token = "alskdjfhaslkdfjhaslkdfjh"
