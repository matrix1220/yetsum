import os.path
debug = os.path.exists("debug")

import logging
if debug:
	logging.basicConfig(level=logging.DEBUG)
else:
	logging.basicConfig(filename='app.log', filemode='w', level=logging.ERROR)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker as _sessionmaker

if debug:
	engine = create_engine('sqlite:///database.db')
else:
	engine = create_engine('mysql+mysqlconnector://root:kNG7Dm2yC6dGfAD3AVkYjtYh_@localhost/qmarket', pool_size=20)
	
sessionmaker = _sessionmaker(bind=engine)