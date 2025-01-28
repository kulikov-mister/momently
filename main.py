import asyncio
import logging
from loader import dp, bot
import handlers


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format="%(name)s %(asctime)s %(levelname)s %(message)s")
    asyncio.run(main())
