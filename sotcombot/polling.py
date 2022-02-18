from config import bot
from bot import handle
import asyncio

# async def main():
# 	asyncio.create_task(bot.message_queue.exec())
# 	await bot.long_polling(handle)

ioloop = asyncio.get_event_loop()
# ioloop.create_task(main())
tasks = [ioloop.create_task(bot.long_polling(handle)), ioloop.create_task(bot.message_queue.exec())]
wait_tasks = asyncio.wait(tasks)
ioloop.run_until_complete(wait_tasks)
ioloop.close()

#asyncio.run(main())