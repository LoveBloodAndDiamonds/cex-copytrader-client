import time
from datetime import datetime
from threading import Thread
from typing import Callable, Literal, Optional

from .abstract import AbstractService
from .connectors import EXCHANGE_TO_POLLING_SERVICE, AbstractExchangeConnector
from ..configuration import logger, config
from ..schemas.enums import BalanceStatus
from ..schemas.models import UserSettings, TraderSettings
from ..schemas.types import ServiceStatus


class TraderPollingService(AbstractService, Thread):
    """
    Класс, который отвечает за сравнение ордеров и позиций клиента и трейдера.
    """

    def __init__(
            self,
            connector_factory: Callable[[Literal["trader", "client"]], Optional[AbstractExchangeConnector]],
            user_settings: UserSettings,
            trader_settings: TraderSettings,
            interval: int | float = config.TRADER_POLLING_INTERVAL
    ) -> None:
        AbstractService.__init__(self)
        Thread.__init__(self, daemon=True)

        self._connector_factory: Callable[[Literal["trader", "client"]], Optional[AbstractExchangeConnector]] = \
            connector_factory
        self._user_settings: UserSettings = user_settings
        self._trader_settings: TraderSettings = trader_settings
        self._balance_status: BalanceStatus = BalanceStatus.NOT_DEFINED

        self._interval: int | float = interval

        self._last_update_time: int | float = 0.00  # for status

    def get_status(self) -> ServiceStatus:
        return ServiceStatus(
            status=self._check_statuses(),
            last_update_time=datetime.fromtimestamp(self._last_update_time).isoformat(timespec='seconds')
        )

    get_status.__doc__ = AbstractService.get_status.__doc__

    def run(self) -> None:
        """ Service entry point """
        while True:
            try:
                if not self._check_statuses():
                    continue

                self._last_update_time = time.time()

                EXCHANGE_TO_POLLING_SERVICE[self._trader_settings.exchange].process(
                    connector_factory=self._connector_factory,
                    user_settings=self._user_settings
                )

            except Exception as e:
                logger.error(f"Error in trader pollong service: {e}")
            finally:
                time.sleep(self._interval)

    def _check_statuses(self) -> bool:
        """ Функция проверяет все статусы и переменные, перед тем как дать разрешение на продолжение работы. """
        result: bool = True
        if not self._connector_factory("client"):
            logger.debug("Can not proceed polling becouse client connector factory")
            result = False
        if not self._connector_factory("trader"):
            logger.debug("Can not proceed polling becouse trader connector factory")
            result = False
        if not self._user_settings.status:
            logger.debug("Can not proceed polling becouse _user_settings.status")
            result = False
        if not self._trader_settings.status:
            logger.debug("Can not proceed polling becouse _trader_settings.status")
            result = False
        if self._balance_status != BalanceStatus.CAN_TRADE:
            logger.debug("Can not proceed polling becouse _balance_status")
            result = False
        return result

    def on_balance_status_update(self, balance_status: BalanceStatus):
        logger.info(f"Balance status update: {balance_status}")
        self._balance_status = balance_status

    def on_user_settings_update(self, u: UserSettings) -> None:
        logger.info(f"User settings update event: {u}")
        self._user_settings: UserSettings = u

    def on_trader_settings_update(self, u: TraderSettings) -> None:
        logger.info(f"Trader settings update event: {u}")
        self._trader_settings: TraderSettings = u
