import re

def converter(string):
	try:
		return int(string)
		if string == "None": return None
	except ValueError:
		return string

def unescape(items):
	return [converter(x.replace('\\-','-')) for x in re.split(r'(?<!\\)-', items)]
def escape(*items):
	return "-".join(str(x).replace('-', '\\-') for x in items)

def format(data, **kwargs):
	if isinstance(data, list):
		for x, y in enumerate(data): data[x] = format(y, **kwargs)
	elif isinstance(data, dict):
		for x, y in data.items(): data[x] = format(y, **kwargs)
	elif isinstance(data, str):
		return data.format(**kwargs)
	return data
