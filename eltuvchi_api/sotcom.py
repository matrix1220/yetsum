import requests
from object_dict import objectify, dictify

class SotCom:
	#API_URL = 'http://192.168.1.164:5000/'
	#API_URL = 'https://api.sotuvchi.com/'

	class _helper:
		def __init__(self, instance, method_type):
			self.instance = instance
			self.method_type = method_type

		def __getattr__(self, method):
			def function(**kwargs):
				return self.instance.send(self.method_type, method, kwargs)
			return function

	def __init__(self, token=None):
		self.token = token
		for x in ['get', 'post']:
			setattr(self, x, self._helper(self, x))

	def send(self, method_type, method, data):
		#print(self.API_URL + method, data)
		response = getattr(requests, method_type)(self.API_URL + method, json=data, headers={"token": self.token})
		#print(response.status_code)
		#print(response.content)
		data = objectify(response.json())
		#print(response.data)
		if not data.ok: raise Exception(data.err_str)
		return data.result
		
# 
sotcom = SotCom("5154644") # 5154644 # 212114881
# 108268232
print(sotcom.get.Orders(district_id=1))
#import datetime
#tmp = sotcom.get.DailyStats()
#print(tmp)
#print(datetime.datetime.fromtimestamp(tmp[0].date))
#print(sotcom.get.Filters())

#print(sotcom.get.Courier(telegram_id=108268232))
#print(sotcom.post.OrderStatus(order_id=41009, status=1))
#print(sotcom.post.OrderStatus(courier_id=123123123123, order_id=1232347523475, status=1))
#print(sotcom.get.ActiveOrder(order_id=42852))
#print(sotcom.get.WeeklyStats(courier_id=15))
#a,b,c = sotcom.get.ActiveOrder(order_id=42852)
#print("asd: {c}".format(c=c.name if c else None))