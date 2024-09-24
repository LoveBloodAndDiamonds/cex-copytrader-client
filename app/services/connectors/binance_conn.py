from abc import ABC

from binance import Client

from app.schemas.enums import Exchange
from .abstract import AbstractExchangeConnector


class BinanceConnector(AbstractExchangeConnector):

    def __init__(self, api_key: str, api_secret: str, exchange: Exchange) -> None:
        super().__init__(api_key=api_key, api_secret=api_secret, exchange=exchange)

        self._client: Client = Client(api_key=api_key, api_secret=api_secret)

    def get_current_balance(self) -> float:
        """ Returns current user balance. """
        for asset in self._client.futures_account_balance():
            if asset["asset"] == "USDT":
                return float(asset["availableBalance"])

    def get_all_open_positions(self) -> list[dict]:
        """ Returns list of opened positions """
        return self._client.futures_account()["positions"]

    def get_all_open_orders(self) -> list[dict]:
        """ Returns list of opened orders """
        raise NotImplementedError

    def create_order(self, **params) -> None:
        """ Create order """
        raise NotImplementedError

    def cancel_order(self, order_id: int | str) -> None:
        """ Cancel order by id """
        raise NotImplementedError

    def cancel_all_open_orders(self) -> None:
        """ Cancel all opened orders """
        raise NotImplementedError

    def close_all_open_positions(self) -> None:
        """ Cancel all opened positions """
        raise NotImplementedError
