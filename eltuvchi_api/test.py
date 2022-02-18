# from sshtunnel import SSHTunnelForwarder
# server =  SSHTunnelForwarder(
# 	('78.47.105.80', 253),
# 	ssh_password="matrix4",
# 	ssh_username="matrix",
# 	remote_bind_address=('127.0.0.1', 3306)
# )
# server.start()

# print(server.local_bind_port)
# import json
# tmp = {}
# tmp[5] = 'asd'
# print(json.dumps(tmp))

import re

print(re.match(r"(\+?998)?(?P<phone>\d{9})$", "123456789"))
#test = 'asd'
#print(test[-2:])
print(re.match(r"^/id(\d*)$", "/id123456789").group(1))