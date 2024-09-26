import time
from datetime import datetime
from threading import Thread
from typing import Callable, Optional, Literal

from .abstract import AbstractService
from .connectors import AbstractExchangeConnector
from ..configuration import config, logger
from ..schemas.types import ServiceStatus


class BalanceUpdaterService(AbstractService, Thread):

    def __init__(
            self,
            connector_factory: Callable[[Literal["trader", "client"]], Optional[AbstractExchangeConnector]],
            balance_changed_callbacks: list[Callable[[float], None]],
            interval: int | float = config.BALANCE_UPDATE_INTERVAL
    ) -> None:
        """
        :param connector_factory: Фабрика коннектора с биржей.
        :param balance_changed_callbacks: Куда передавать баланс при обновлении.
        """
        AbstractService.__init__(self)
        Thread.__init__(self, daemon=True)

        self._connector_factory: Callable[[Literal["trader", "client"]], Optional[AbstractExchangeConnector]] \
            = connector_factory
        self._balance_changed_callbacks: list[callable] = balance_changed_callbacks

        self._interval: int | float = interval
        self._last_update_time: int | float = 0.00  # for status

    def get_status(self) -> ServiceStatus:
        return ServiceStatus(
            status=self._last_update_time + 60 > time.time(),
            last_update_time=datetime.fromtimestamp(self._last_update_time)
        )

    get_status.__doc__ = AbstractService.get_status.__doc__

    def run(self) -> None:
        """ Точка запуска сервиса. """
        debug_log_sent: bool = False
        while True:
            try:
                connector: AbstractExchangeConnector | None = self._connector_factory("client")
                if connector:
                    debug_log_sent: bool = False
                    try:
                        balance: float = connector.get_current_balance()
                    except Exception as e:
                        logger.error(f"Error while gettings balance: {e}")
                    else:
                        for callback in self._balance_changed_callbacks:
                            try:
                                self._last_update_time = time.time()
                                callback(balance)
                            except Exception as e:
                                logger.error(f"Error while called callback({callback.__name__}): {e}")
                else:
                    if not debug_log_sent:
                        logger.debug("Can't send balance, becouse connector are not inited")
                        debug_log_sent: bool = True
            except Exception as e:
                logger.error(f"Error while update balance: {e}")
            finally:
                time.sleep(self._interval)
