__all__ = [
    "EXCHANGE_TO_CONNECTOR", "AbstractExchangeConnector",
    "EXCHANGE_TO_POLLING_SERVICE", "AbstractPollingService",
    "EXCHANGE_TO_WEBSOCKET", "AbstractTraderWebsocket"
]

from app.schemas.enums import Exchange

from .abstract import *
from .binance_conn import *

EXCHANGE_TO_CONNECTOR: dict[Exchange | str, type[AbstractExchangeConnector]] = {
    Exchange.BINANCE: BinanceConnector,
    Exchange.BINANCE.value: BinanceConnector,
}

EXCHANGE_TO_POLLING_SERVICE: dict[Exchange | str, type[AbstractPollingService]] = {
    Exchange.BINANCE: BinancePollingService,
    Exchange.BINANCE.value: BinancePollingService,
}

EXCHANGE_TO_WEBSOCKET: dict[Exchange | str, type[AbstractTraderWebsocket]] = {
    Exchange.BINANCE: BinanceTraderWebsocket,
    Exchange.BINANCE.value: BinanceTraderWebsocket,
}
