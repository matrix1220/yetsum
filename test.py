
#import requests_async as requests

# async def main():
# 	print("start")
# 	result = await requests.post('https://api.telegram.org/bot532062536:AAE4EsWPbDotBzt_n_oInowMcMY53vO_6-s/getme')
# 	print(result.content)
# 	print("end")

# import asyncio

# asyncio.run(main())

import requests
print("start12")
result = requests.post('https://api.telegram.org/bot532062536:AAE4EsWPbDotBzt_n_oInowMcMY53vO_6-s/sendchataction?chat_id=108268232&action=typing')
print(result.content)
print("end")