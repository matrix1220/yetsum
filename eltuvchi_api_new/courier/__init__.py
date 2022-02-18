
from starlette.responses import JSONResponse
from starlette.routing import Route
from config import sessionmaker
from dbscheme import Courier
import traceback

routes = []

class Context:
	pass


def error(err_str, **kwargs):
	return JSONResponse({"ok":False, "err_str": err_str, **kwargs})

def ok(result, **kwargs):
	return JSONResponse({"ok":True, "result":result, **kwargs})

async def func(request):
	if "token" not in request.headers:
		return error("you are not good enough to use this api")

	token = request.headers["token"]

	db = sessionmaker()

	context = Context()
	context.request = request
	context.db = db
	tmp = dict(await request.json())
	if "method" not in tmp or "data" not in tmp:
		return error("structure error")

	context.data = tmp['data']
	if tmp['method'] not in endpoints:
		return error("method not found error")

	courier = db.query(Courier).filter_by(token=token).first()
	if not courier:
		return error("courier not found")
	context.courier = courier

	try:
		result = await endpoints[tmp['method']](context, **context.data)
		db.commit()
		return ok(result)
	except Exception as e:
		return error(str(e), trace=traceback.format_exc())




routes.append(Route("/courier", func))

def register(endpoint):
	endpoints[endpoint.__name__] = endpoint

endpoints = {}

from . import order
