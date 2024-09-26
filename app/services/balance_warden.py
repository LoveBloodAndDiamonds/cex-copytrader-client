import time
from datetime import datetime
from typing import Callable, Literal, Optional

from .abstract import AbstractService
from .connectors import AbstractExchangeConnector
from ..configuration import logger
from ..schemas.enums import BalanceStatus
from ..schemas.models import UserSettings
from ..schemas.types import Order, Position, ServiceStatus


class BalanceWardenService(AbstractService):
    """
    Класс проверяет текущий баланс пользователя с порогом баланса для отключения торговли.
    """

    def __init__(
            self,
            connector_factory: Callable[[Literal["trader", "client"]], Optional[AbstractExchangeConnector]],
            balance_threshold: float,
            balance_status_callbacks: list[Callable[[BalanceStatus], None]]
    ) -> None:
        """
        :param balance_threshold: Настройки пользователя
        """
        AbstractService.__init__(self)

        self._connector_factory: Callable[[Literal["trader", "client"]], Optional[AbstractExchangeConnector]] = \
            connector_factory
        self._balance_threshold: float = balance_threshold
        self._balance_status_callbacks: list[Callable[[BalanceStatus], None]] = balance_status_callbacks

        # Используется чтобы не вызывать функции много раз попусту
        self._balance_status: BalanceStatus = BalanceStatus.NOT_DEFINED

        self._last_update_time: int | float = 0.00  # for status

    def get_status(self) -> ServiceStatus:
        return ServiceStatus(
            status=self._balance_status == BalanceStatus.CAN_TRADE and self._last_update_time + 60 > time.time(),
            last_update_time=datetime.fromtimestamp(self._last_update_time)
        )

    get_status.__doc__ = AbstractService.get_status.__doc__

    def balance_update_event(self, balance: float) -> None:
        """ Функция принимает текущий баланс пользователя и сравнивает его с порогом баланса. """
        try:
            self._last_update_time = time.time()
            if balance < self._balance_threshold and self._balance_status != BalanceStatus.CANT_TRADE:
                logger.critical(f"Current balance({balance}) lower than balance threshold({self._balance_threshold})!")
                self._change_status(BalanceStatus.CANT_TRADE)
                self._stop_trade_event()
            elif balance > self._balance_threshold and self._balance_status != BalanceStatus.CAN_TRADE:
                logger.success(f"Current balance({balance}) greater than balance threshold({self._balance_threshold})!")
                self._change_status(BalanceStatus.CAN_TRADE)
        except Exception as e:
            logger.error(f"Error while warden client balance: {e}")

    def _change_status(self, status: BalanceStatus) -> None:
        try:
            self._balance_status: BalanceStatus = status

            # Send callbacks that app can not trade anymore
            for callback in self._balance_status_callbacks:
                callback(self._balance_status)
        except Exception as e:
            logger.error(f"Error while change services balance status: {e}")

    def _stop_trade_event(self) -> None:
        # Close all orders and positions
        logger.warning("Stop trading event called!")
        connector: AbstractExchangeConnector | None = self._connector_factory("client")
        if connector:
            self._close_all_open_positions(connector)
            self._cancel_all_open_orders(connector)
        else:
            logger.critical("Can not get connector to call stop trading event.")

    def _cancel_all_open_orders(self, connector: AbstractExchangeConnector) -> None:
        """ Cancel all open orders in account """
        try:
            orders: list[Order] = connector.get_all_open_orders()
            symbols: set[str] = set([o["symbol"] for o in orders])
            for symbol in symbols:
                try:
                    result: dict = connector.cancel_all_open_orders(symbol=symbol)
                    logger.info(f"Cancel all open orders on {symbol}: {result}")
                except Exception as e:
                    logger.error(f"Error while canceling all open orders on {symbol}: {e}")
        except Exception as e:
            logger.error(f"Error while canceling all open orders: {e}")

    def _close_all_open_positions(self, connector: AbstractExchangeConnector) -> None:
        """ Cancel all open positions in account """
        try:
            positions: list[Position] = connector.get_all_open_positions()
            for position in positions:
                try:
                    result: dict = connector.close_position(position=position)
                    logger.info(f"Closing position {position}: {result}")
                except Exception as e:
                    logger.error(f"Error while closing position {position}: {e}")
        except Exception as e:
            logger.error(f"Error while canceling all open positions: {e}")

    def on_user_settings_update(self, user_settings: UserSettings) -> None:
        """ Функция обновляет порог баланса. """
        self._balance_status: BalanceStatus = BalanceStatus.NOT_DEFINED
        self._balance_threshold: float = user_settings.balance_threshold
