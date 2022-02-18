
from sqlalchemy.sql import func
from . import api

@register
async def GetFiltersAll(context):
	regions = {}
	courier = context.courier
	db = context.db

	if courier.regions:
		query = db.query(Region)\
			.filter(Region.id.in_( courier.regions.split('-') ))\
			.join(func.count(Order.id), and_(
					Order.region_id==Region.id,
					Order.status==1,
					Order.courier==None
			))
		for region, count in query:
			regions[region.id] = {
				"name": region.name,
				"count": count
			}

	districts = {}
	if courier.districts:
		query = db.query(District)\
			.filter(District.id.in_( courier.districts.split('-') ))\
			.join(func.count(Order.id), and_(
					Order.district_id==District.id
					Order.status==1,
					Order.courier==None
			))
		for district, count in query:
			districts[district.id] = {
				"name": district.name,
				"count": count
			}
	mine = db.query(Order).filter(and_(Order.status==1, Order.courier==courier.id)).count()
	return {"regions":regions, "districts":districts, "mine":f"{mine}/{courier.limet}" }


@register
async def GetFiltersRegion(context):
	courier = context.courier
	if not courier.regions: raise Exception("asd")
	if region_id not in courier.regions.split('-'): raise Exception("asd")

	districts = {}
	query = context.db.query(District)\
		.filter(District.region_id==region_id)\
		.join(func.count(Order.id), and_(
				Order.district_id==District.id
				Order.status==1,
				Order.courier==None
		))
	for district, count in query:
		districts[district.id] = {
			"name": district.name,
			"count": count
		}

	return districts