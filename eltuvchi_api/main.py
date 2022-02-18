from werkzeug.wrappers import Request, Response
from werkzeug.exceptions import HTTPException, NotFound

from config import token, db
from dbscheme import Courier
from dbscheme import row_as_dict
from object_dict import objectify, dictify
import json, datetime, time, decimal

import methods

class CustomEncoder(json.JSONEncoder):
    def default(self, data):
        if isinstance(data, datetime.datetime):
            return data.timestamp()
        elif isinstance(data, datetime.date):
            return time.mktime(data.timetuple())
        elif isinstance(data, decimal.Decimal):
            return float(data)
        elif isinstance(data, db.base):
            return row_as_dict(data)
        else:
            return super().default(data)

def json_dumps(data):
	return json.dumps(data, cls=CustomEncoder)

class JSONException(HTTPException):
	def get_headers(self, environ = None):
		return [("Content-Type", "application/json; charset=utf-8")]

	def get_body(self, environ = None):
		return json_dumps({"ok":False, "code":self.code, "err_str":self.description})
		#{self.code} {escape(self.name) self.get_description(environ)

class JSONNotFound(NotFound, JSONException):
	pass

class JSONResponse(Response):
	def __init__(self, response):
		Response.__init__(self, json_dumps({"ok":True, "result":response}))


def check_types(data, types):
	for x, y in types.items():
		if x not in data or type(data[x])!=y: 
			return False

	return True

@Request.application
def application(request):
	session = db.sessionmaker()

	try:
		return handle(session, request)
	except JSONException as e:
		raise e
	except Exception as e:
		raise JSONException(str(e))
	finally:
		try:
			session.commit()
		except Exception as e:
			session.rollback()
			raise JSONException(str(e))
			#print(e)
		finally:
			session.close()

def handle(session, request):
	if "token" not in request.headers:
		raise JSONNotFound()
	_token = request.headers['token']
	if not _token: raise JSONNotFound()

	data = objectify(json.loads(request.data.decode()))

	method_name = request.method.lower() + request.path[1:]
	if hasattr(methods, method_name):
		method = getattr(methods, method_name)
	else:
		raise JSONNotFound()

	if _token == token:
		if not hasattr(method, "privileged_execute"): raise JSONNotFound()
		if hasattr(method, "privileged_execute_arguments"):
			if not check_types(data, method.privileged_execute_arguments):
				raise JSONNotFound()

		return JSONResponse(method.privileged_execute(session, data))
	else:
		courier = session.query(Courier).filter(Courier.token==_token).first()
		if not courier: raise JSONNotFound()
		if courier.status!='1': raise JSONNotFound()
		if not hasattr(method, "execute"): raise JSONNotFound()

		courier.session = session

		if hasattr(method, "execute_arguments"):
			if not check_types(data, method.execute_arguments):
				raise JSONNotFound()

		return JSONResponse(method.execute(courier, data))

	raise JSONNotFound()

if __name__ == '__main__':
    #from werkzeug.serving import run_simple
    #run_simple('0.0.0.0', 5000, application, use_debugger=False, use_reloader=False)
    pass
