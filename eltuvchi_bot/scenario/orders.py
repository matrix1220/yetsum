from photon import OutlineMenu, InlineMenu
from photon.objects import Message
from photon import key, act, explicit_act
from dbsite import Order, Region, District
from sqlalchemy import and_, or_
from photon.client import inline_button
from sqlalchemy.sql import func

from .order import Order as Order_

class Orders(InlineMenu):
	async def _act(self):
		#user = self.context.user
		courier = self.context.courier
		db = self.context.dbmain
		self.keyboard = []
		opened_count = db.query(Order).filter(Order.status==1, Order.courier_id==courier.id).count()
		self.keyboard.append([(f"Meniki ({opened_count}/{courier.limet})", key("opened") )])

		if courier.regions:
			query = db.query(Region, func.count(Order.id))\
				.filter(Region.id.in_( courier.regions.split('-') ))\
				.join(Order, and_(
						Order.region_id==Region.id,
						Order.status==1,
						Order.courier_id==None
				))
			for region, count in query:
				if not region: continue
				self.keyboard.append([(f"{region.name} ({count})", key("region", region.id) )])

		if courier.districts:
			query = db.query(District, func.count(Order.id))\
				.filter(District.id.in_( courier.districts.split('-') ))\
				.join(Order, and_(
						Order.district_id==District.id,
						Order.status==1,
						Order.courier_id==None
				))
			for district, count in query:
				if not district: continue
				self.keyboard.append([(f"{district.name} ({count})", key("district", district.id) )])


		self.register()
		return Message("Tanlang")

	async def handle_key_region(self, region_id):
		self.keyboard = []
		if not self.context.courier.regions: return "error 1"
		if str(region_id) not in self.context.courier.regions.split('-'): return "error 2"
		orders_count = self.context.dbmain.query(Order).filter(
			Order.region_id==region_id,
			Order.status==1,
			Order.courier_id==None,
		).count()
		if orders_count<20:
			orders = self.context.dbmain.query(Order).filter(
				Order.region_id==region_id,
				Order.status==1,
				Order.courier_id==None,
			).all()
			return await self.show(orders)

		query = self.context.dbmain.query(District, func.count(Order.id))\
			.filter(District.region_id==region_id)\
			.join(Order, and_(
					Order.district_id==District.id,
					Order.status==1,
					Order.courier_id==None
			))
		for district, count in query:
			if not district: continue
			self.keyboard.append([
				(f"{district.name} ({count})", key("region_district", district.region_id, district.id) )
			])

		return True
		#keyboard.append([inline_button(language.all, [Orders.WholeRegion.id, region_id] )])

	async def handle_key_opened(self):
		orders = self.context.dbmain.query(Order).filter(
			Order.courier_id==self.context.courier.id, Order.status==1
		).all()
		return await self.show(orders)

	# async def handle_key_all(self):
	# 	orders = orders()
	# 	return await self.show(user, orders)

	async def handle_key_district(self, district_id):
		if not self.context.courier.districts: return "error"
		if str(district_id) not in self.context.courier.districts.split('-'): return "error"
		orders = self.context.dbmain.query(Order).filter(
			Order.district_id==district_id,
			or_(Order.courier_id==None, Order.courier_id==self.context.courier.id),
			Order.status==1
		).all()
		return await self.show(orders)

	# async def handle_key_whole_region(self, region_id):
	# 	orders = orders(region_id=region_id)
	# 	return await self.show(user, orders)

	async def handle_key_region_district(self, region_id, district_id):
		if not self.context.courier.regions: return "error"
		if str(region_id) not in self.context.courier.regions.split('-'): return "error"
		# if not self.context.courier.districts: return "error"
		# if str(district_id) not in self.context.courier.districts.split('-'): return "error"

		orders = self.context.dbmain.query(Order).filter(
			Order.region_id==region_id,
			Order.district_id==district_id,
			or_(Order.courier_id==None, Order.courier_id==self.context.courier.id),
			Order.status==1
		).all()
		return await self.show(orders)

	async def show(self, orders):
		if len(orders)==0:
			return Message("Sizning so'rovingiz bo'yicha buyurtma topilmadi.")

		order =  orders.pop(0)
		#print(order)
		await self.exec(await self.context.explicit_act(Order_, order))
		print(self.context.menu_stack.current())
		
		if len(orders)==0: return
		context = self.context.switch_mode()
		for order in orders:
			context_ = context.switch_mode()
			await self.exec(await context_.explicit_act(Order_, order))
			#context_.commit()
			#await asyncio.sleep(0.1)