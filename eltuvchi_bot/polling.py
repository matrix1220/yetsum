from config import bot
import asyncio
import scenario

async def main():
	await bot.long_polling()

# ioloop = asyncio.get_event_loop()
# ioloop.run_until_complete(ioloop.create_task(main()))
# ioloop.close()

asyncio.run(main())