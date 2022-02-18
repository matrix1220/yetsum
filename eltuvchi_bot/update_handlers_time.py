import time

with open('least_handlers_time', 'w') as writer:
	writer.write(str(int(time.time())))