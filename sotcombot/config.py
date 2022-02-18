
import os.path
debug = os.path.exists("debug")

import logging
if debug:
	logging.basicConfig(level=logging.DEBUG)
else:
	#logging.basicConfig(level=logging.DEBUG)
	FORMAT = '%(asctime)s;%(levelname)s;%(message)s'
	logging.basicConfig(format=FORMAT, filename='app.log', filemode='w', level=logging.ERROR)

# 359269508:AAE5TKgX3f2VC5gNxaUztSTxThswsRr_BIk
# 287925905:AAEsaBOKVGoKDiGxBr1aaBxkpYn4AHUpbJQ dev botmoq
# 305643264:AAGwALg3QDiH2OrNzqehgoPdeXwpIqY416c dev aybir
# 1439060825:AAGp1-jD1KunOffsw2d-xP1npEkIxg_PMww prod
# 532062536:AAE4EsWPbDotBzt_n_oInowMcMY53vO_6-s
if debug:
	token = "287925905:AAEsaBOKVGoKDiGxBr1aaBxkpYn4AHUpbJQ"
else:
	token = "1439060825:AAGp1-jD1KunOffsw2d-xP1npEkIxg_PMww"

from photon import Bot
bot = Bot(token)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker as _sessionmaker
from sqlalchemy.ext.declarative import declarative_base


from sotcom import SotCom
sotcom = SotCom("alskdjfhaslkdfjhaslkdfjh")
filter_names = sotcom.get.FilterNames()

class db:
	engine = create_engine('sqlite:///datebase.db')
	sessionmaker = _sessionmaker(bind=engine)
	base = declarative_base()
	session = sessionmaker()

import dbscheme
db.base.metadata.create_all(db.engine)

import yaml
from object_dict import objectify

language = objectify(yaml.load(open('language_uz.yaml').read(), Loader=yaml.Loader))

statuses = objectify({4:{"channel":-1001476356831, "symbol":"✅"}, 3:{"channel":-1001285547213, "symbol":"♻️"}}) #5:-1001176286222

with open('least_handlers_time', 'r') as reader:
	least_handlers_time = int(reader.read())