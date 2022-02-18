
routes = []

class Context:
	pass

from starlette.responses import JSONResponse

def error(err_str, **kwargs):
	return JSONResponse({"ok":False, "err_str": err_str, **kwargs})

def ok(result, **kwargs):
	return JSONResponse({"ok":True, "result":result, **kwargs})

async def func(request):
	if "token" not in request.headers:
		return error("you are not good enough to use this api")
	token = request.headers["token"]
	if token!=_token:
		return error("you are not good enough to use this token")

	db = sessionmaker()
	context = Context()
	context.request = request
	context.db = db
	tmp = dict(await self.request.json())
	if "method" not in tmp or "data" not in tmp:
		return error("structure error")
	context.data = tmp['data']
	try:
		result = await endpoints[tmp['method']](**context.data)
		db.commit()
		return ok(result)
	except Exception as e:
		return error(str(e), trace=traceback.format_exc())

from starlette.routing import Route

_token = "secret_token"

routes.append(Route(f"/priviliged", func))

def register(endpoint):
	endpoints[endpoint.__name__] = endpoint

endpoints = {}




# class getCourier:
# 	privileged_execute_arguments = {"telegram_id":int}
# 	def privileged_execute(session, data):
# 		courier = session.query(Courier).filter(Courier.telegram_id==data.telegram_id).first()
# 		if not courier: return False
# 		if courier.status!='1': return False
# 		return row_as_dict(courier)