import asyncio
import logging

from database.models import Base, engine

logging.basicConfig(filename='parser.log', level=logging.INFO, format='%(levelname)s %(asctime)s %(message)s')


async def init_models():
    logging.info('Init database models')
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

if __name__ == '__main__':
    asyncio.run(init_models())
