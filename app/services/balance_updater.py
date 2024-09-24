import time
from threading import Thread
from typing import Callable, Optional

from .connectors import AbstractExchangeConnector
from ..configuration import config, logger


class BalanceUpdaterService(Thread):

    def __init__(
            self,
            connector_factory: Callable[[], Optional[AbstractExchangeConnector]],
            callbacks: list[Callable[[float], None]],
            interval: int | float = config.BALANCE_UPDATE_INTERVAL
    ) -> None:
        """
        :param connector_factory: Фабрика коннектора с биржей.
        :param callbacks: Куда передавать баланс при обновлении.
        """
        super().__init__(daemon=True)

        self._connector_factory: Callable[[], Optional[AbstractExchangeConnector]] = connector_factory
        self._callbacks: list[callable] = callbacks

        self._interval: int | float = interval

    def run(self) -> None:
        """ Точка запуска сервиса. """
        debug_log_sent: bool = False
        while True:
            try:
                connector: AbstractExchangeConnector | None = self._connector_factory()
                if connector:
                    debug_log_sent: bool = False
                    try:
                        balance: float = connector.get_current_balance()
                    except Exception as e:
                        logger.error(f"Error while gettings balance: {e}")
                    else:
                        for callback in self._callbacks:
                            try:
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
