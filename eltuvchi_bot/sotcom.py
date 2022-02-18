import requests
from object_dict import objectify, dictify
import logging
logger = logging.getLogger('sotcom')

#from config import debug

class SotCom:
	API_URL = 'http://127.0.0.1:8080/'
	#API_URL = 'http://168.119.118.220:8080/'
	#API_URL = 'https://api.sotuvchi.com/'

	class _helper:
		def __init__(self, instance, method_type):
			self.instance = instance
			self.method_type = method_type

		def __getattr__(self, method):
			def function(**kwargs):
				return self.instance.send(self.method_type, method, kwargs)
			return function

	def __init__(self, token):
		self.token = token
		for x in ['get', 'post']:
			setattr(self, x, self._helper(self, x))

	def send(self, method_type, method, data):
		logger.debug([self.API_URL + method, self.token, data])
		response = getattr(requests, method_type)(self.API_URL + method, json=data, headers={"token": self.token})
		data = objectify(response.json())
		logger.debug(data)
		#if response.status_code!=200: raise Exception(data.err_str)
		if not data.ok: raise Exception(data.err_str)
		return data.result
		

#sotcom = SotCom("alskdjfhaslkdfjhaslkdfjh")

#print(sotcom.get.Courier(telegram_id=181040037))
#print(sotcom.get.Courier(telegram_id=108268232))

#print(sotcom.get.Districts(region="Xorazm"))
#print(sotcom.get.ActiveOrders(region="Xorazm"))
#print(sotcom.get.ActiveCourier(telegram_id=108268232))
#print(sotcom.post.OrderStatus(order_id=41009, status=1))
#print(sotcom.post.OrderStatus(courier_id=123123123123, order_id=1232347523475, status=1))
#print(sotcom.get.ActiveOrder(order_id=42852))
#print(sotcom.get.WeeklyStats(courier_id=15))
#print(sotcom.get.DailyStats(courier_id=15))

# 54546546546465
# 00000
#sotcom = SotCom("54546546546465")
#print(sotcom.get.me())
#print(sotcom.get.Order(order_id=1))
#print(sotcom.get.Orders(region_id=1))
#print(sotcom.get.Orders(district_id=28))
#print(sotcom.get.Filters())
#print(sotcom.get.DailyStats())
#print(sotcom.get.WeeklyStats())
#print(sotcom.get.Offers())
# for tmp in sotcom.get.Offers():
# 	print(tmp.short_name, tmp.price, tmp.name)



#print(text)