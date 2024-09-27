"""
Module that rounds prices and quantities for symbols
"""
__all__ = ["exchange_info", ]

import re
import time

import requests

from app.configuration import logger
from ..abstract import AbstractExchangeInfo


class ExchangeInfo(AbstractExchangeInfo):
    precisions: dict[str: list[int, int]] = {}

    @classmethod
    def run(cls) -> None:
        while True:
            try:
                response: requests.Response = requests.get(url="https://fapi.binance.com/fapi/v1/exchangeInfo")
                exchange_info_dict: dict = response.json()
                for i in exchange_info_dict['symbols']:
                    filters = i['filters']
                    tick_size, step_size = None, None
                    for f in filters:
                        if f['filterType'] == 'PRICE_FILTER':
                            tick_size = f['tickSize']
                            tick_size = list(re.sub('0+$', '', tick_size))
                            if len(tick_size) == 1:
                                tick_size = 1
                            else:
                                tick_size = len(tick_size) - 2
                        if f['filterType'] == 'MARKET_LOT_SIZE':
                            step_size = f['stepSize']
                            step_size = list(re.sub('0+$', '', step_size))
                            if len(step_size) == 1:
                                step_size = 0
                            else:
                                step_size = len(step_size) - 2
                        cls.precisions[i['symbol'].upper()] = {
                            "price": tick_size,
                            "quantity": step_size
                        }

            except Exception as e:
                logger.error(f"Preisions error: {e}")
            time.sleep(60 * 60)

    @classmethod
    def round_price(cls, symbol: str, price: float) -> float:
        """
        Round price
        :param symbol:
        :param price:
        :return:
        """
        try:
            return round(price, cls.precisions[symbol.upper()]["price"])
        except KeyError as e:
            logger.error(f"KeyError while rounding price {symbol}: {e}")

    @classmethod
    def round_quantity(cls, symbol: str, quantity: float) -> float:
        """
        Round quantity
        :param symbol:
        :param quantity:
        :return:
        """
        try:
            return round(quantity, cls.precisions[symbol.upper()]["quantity"])
        except KeyError as e:
            logger.error(f"KeyError while rounding quantity {symbol}: {e}")
            return quantity


exchange_info = ExchangeInfo()
exchange_info.start()
