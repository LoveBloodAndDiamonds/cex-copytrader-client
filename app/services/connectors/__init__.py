__all__ = ["EXCHANGE_TO_CONNECTOR", "EXCHANGE_TO_POLLING_SERVICE", "EXCHANGE_TO_WEBSOCKET",
           "AbstractExchangeConnector", "AbstractPollingService"]

from app.schemas.enums import Exchange

from .abstract import AbstractExchangeConnector, AbstractExchangeInfo, AbstractPollingService
from .binance_conn import BinanceConnector, binance_exchange_info, BinancePollingService

EXCHANGE_TO_EXCHANGE_INFO: dict[Exchange | str, AbstractExchangeInfo] = {
    Exchange.BINANCE: binance_exchange_info,
    Exchange.BINANCE.value: binance_exchange_info,
}

EXCHANGE_TO_CONNECTOR: dict[Exchange | str, type[AbstractExchangeConnector]] = {
    Exchange.BINANCE: BinanceConnector,
    Exchange.BINANCE.value: BinanceConnector,
}

EXCHANGE_TO_POLLING_SERVICE: dict[Exchange | str, type[AbstractPollingService]] = {
    Exchange.BINANCE: BinancePollingService,
    Exchange.BINANCE.value: BinancePollingService,
}

EXCHANGE_TO_WEBSOCKET: dict[Exchange | str, type[None]] = {

}
