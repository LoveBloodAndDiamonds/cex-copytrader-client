import asyncio

import aiohttp
from loguru import logger

from .schemas.exceptions import MasterServerConnectionError
from .schemas.models import UserBalanceUpdate, TraderSettings, UserSettings
from .schemas.types import M

VERSION: float = 1.0
url: str = f"http://127.0.0.1:8000"


class MasterWebsocket:

    def __init__(self):
        self.balance = 0

    async def balance_task(self):
        while True:
            async with aiohttp.ClientSession() as session:
                self.balance += 1
                response: aiohttp.ClientResponse = await session.post(
                    url=url + "/balance",
                    data=UserBalanceUpdate(balance=self.balance).model_dump_json()
                )
                logger.info(f"balance update: {response}")
                await asyncio.sleep(5)

    async def request_model(self, endpoint: str, model: M, session: aiohttp.ClientSession) -> type[M]:
        response: aiohttp.ClientResponse = await session.get(url=url + f"/{VERSION}" + endpoint)

        if response.status == 200:
            return model(**(await response.json()))
        raise MasterServerConnectionError(
            status_code=response.status,
            response_text=await response.text()
        )

        # if response.status == 401:
        #     logger.error(f"Unauthorized: {response}")
        # elif response.status == 405:
        #     logger.error(f"Unsupported version: {response}")
        # elif response.status == 400:
        #     logger.error(f"Can not connect to master server: {response}")

    async def run(self):
        """
        Получаем сообщения с вебсокета с главного сервера.
        :return:
        """
        asyncio.create_task(self.balance_task())

        while True:
            async with aiohttp.ClientSession() as session:
                user_settings: UserSettings = await self.request_model(
                    endpoint="/user_settings",
                    model=UserSettings,
                    session=session
                )

                trader_settings: TraderSettings = await self.request_model(
                    endpoint="/trader_settings",
                    model=TraderSettings,
                    session=session
                )

                logger.info(user_settings)
                logger.info(trader_settings)

                await asyncio.sleep(10)


if __name__ == '__main__':
    asyncio.run(MasterWebsocket().run())
