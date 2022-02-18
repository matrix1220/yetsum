
import os.path
debug = os.path.exists("debug")

import logging
if debug:
	logging.basicConfig(level=logging.DEBUG)
else:
	logging.basicConfig(filename='app.log', filemode='w', level=logging.ERROR)

import photon
if debug:
	bot = photon.Bot("305643264:AAGwALg3QDiH2OrNzqehgoPdeXwpIqY416c")
else:
	bot = photon.Bot("1013987821:AAF8bmXQmkvDl2B4Hx5dxPzqmV1Q-H9xsew")

# import yaml
# from photon.object_dict import objectify

# languages = []
# for x in ['language_uz.yaml']:
# 	languages.append(objectify(yaml.load(open(x).read(), Loader=yaml.Loader)))
