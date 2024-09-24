__all__ = ["EXCHANGE_TO_ADAPTER", "AbstractAdapter", ]

from app.schemas.enums import Exchange
from .abstract import AbstractAdapter
from .binance_adapter import BinanceAdapter

EXCHANGE_TO_ADAPTER: dict[Exchange | str, type[AbstractAdapter]] = {
    Exchange.BINANCE: BinanceAdapter,
    Exchange.BINANCE.value: BinanceAdapter
}
