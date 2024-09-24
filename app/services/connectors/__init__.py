__all__ = ["EXCHANGE_TO_CONNECTOR", "AbstractExchangeConnector"]

from app.schemas.enums import Exchange

from .abstract import AbstractExchangeConnector
from .binance_conn import BinanceConnector


EXCHANGE_TO_CONNECTOR: dict[Exchange | str, type[AbstractExchangeConnector]] = {
    Exchange.BINANCE: BinanceConnector,
    Exchange.BINANCE.value: BinanceConnector,
}
