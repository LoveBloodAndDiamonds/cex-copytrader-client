import time
from threading import Thread
from typing import Callable

from .connectors import EXCHANGE_TO_POLLING_SERVICE, AbstractExchangeConnector
from ..configuration import logger, config
from ..schemas.enums import BalanceStatus
from ..schemas.models import UserSettings, TraderSettings


class TraderPollingService(Thread):
    """
    Класс, который отвечает за сравнение ордеров и позиций клиента и трейдера.
    """

    def __init__(
            self,
            connector_factory: Callable[[], AbstractExchangeConnector],
            trader_connector_factory: Callable[[], AbstractExchangeConnector],
            user_settings: UserSettings,
            trader_settings: TraderSettings,
            interval: int | float = config.TRADER_POLLING_INTERVAL
    ) -> None:
        super().__init__(daemon=True)

        self._connector_factory: Callable[[], AbstractExchangeConnector] = connector_factory
        self._trader_connector_factory: Callable[[], AbstractExchangeConnector] = trader_connector_factory
        self._user_settings: UserSettings = user_settings
        self._trader_settings: TraderSettings = trader_settings
        self._balance_status: BalanceStatus = BalanceStatus.NOT_DEFINED

        self._interval: int | float = interval

    def run(self) -> None:
        """ Service entry point """
        while True:
            try:
                if not self._check_statuses():
                    continue

                EXCHANGE_TO_POLLING_SERVICE[self._trader_settings.exchange].process(
                    client_connector=self._connector_factory(),
                    trader_connector=self._trader_connector_factory(),
                    user_settings=self._user_settings
                )

            except Exception as e:
                logger.error(f"Error in trader pollong service: {e}")
            finally:
                time.sleep(self._interval)

    def _check_statuses(self) -> bool:
        if not self._connector_factory():
            logger.debug("Can not proceed polling becouse _connector_factory")
            return False
        if not self._trader_connector_factory():
            logger.debug("Can not proceed polling becouse _trader_connector_factory")
            return False
        if not self._user_settings.status:
            logger.debug("Can not proceed polling becouse _user_settings.status")
            return False
        if not self._trader_settings.status:
            logger.debug("Can not proceed polling becouse _trader_settings.status")
            return False
        if self._balance_status != BalanceStatus.CAN_TRADE:
            logger.debug("Can not proceed polling becouse _balance_status")
            return False
        return True

    def on_balance_status_update(self, balance_status: BalanceStatus):
        logger.warning(f"Balance status update: {balance_status}")
        self._balance_status = balance_status

    def on_user_settings_update(self, u: UserSettings) -> None:
        logger.warning(f"User settings update event: {u}")
        self._user_settings: UserSettings = u

    def on_trader_settings_update(self, u: TraderSettings) -> None:
        logger.warning(f"Trader settings update event: {u}")
        self._trader_settings: TraderSettings = u
