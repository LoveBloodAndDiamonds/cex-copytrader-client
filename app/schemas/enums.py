from enum import Enum


class Exchange(Enum):
    BINANCE: str = "BINANCE"
    MEXC: str = "MEXC"
    WHITEBIT: str = "WHITEBIT"


class BalanceStatus(Enum):
    CAN_TRADE: str = "CAN_TRADE"
    CANT_TRADE: str = "CANT_TRADE"
    NOT_DEFINED: str = "NOT_DEFINED"
