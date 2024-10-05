import threading
import time
from datetime import datetime
from typing import Callable, Literal, Optional

from .abstract import AbstractService
from .connectors import AbstractExchangeConnector, AbstractTraderWebsocket, EXCHANGE_TO_WEBSOCKET
from ..configuration import logger
from ..schemas.enums import BalanceStatus
from ..schemas.models import UserSettings, TraderSettings
from ..schemas.types import ServiceStatus


class TraderWebsocketService(AbstractService):
    """
    Класс, который отвечает за подключение вебсокетом к трейдеру, и прослушке его сигналов.
    """

    def __init__(
            self,
            connector_factory: Callable[[Literal["trader", "client"]], Optional[AbstractExchangeConnector]],
            user_settings: UserSettings,
            trader_settings: TraderSettings,
    ) -> None:
        super().__init__()

        self._connector_factory: Callable[[Literal["trader", "client"]], Optional[AbstractExchangeConnector]] = \
            connector_factory
        self._user_settings: UserSettings = user_settings
        self._trader_settings: TraderSettings = trader_settings
        self._balance_status: BalanceStatus = BalanceStatus.NOT_DEFINED

        self._websocket: Optional[AbstractTraderWebsocket] = None
        self._next_restart_time: int | float = 0.0  # for restart websocket in while True cycle
        self._restart_interval: int | float = 60 * 60 * 12  # 12 hours
        self._last_message_time: int | float = 0.0  # for logs

        # Launch restart thread one time
        threading.Thread(target=self._restart_thread).start()

    def get_status(self) -> ServiceStatus:
        return ServiceStatus(
            status=self._last_message_time + 60 * 60 * 12 > time.time() and self._check_statuses(),
            last_update_time=datetime.fromtimestamp(self._last_message_time).isoformat(timespec='seconds')
        )

    get_status.__doc__ = AbstractService.get_status.__doc__

    def start(self) -> None:
        """ Запуск соединения с вебсокетом трейдера. """
        if not self._check_statuses():
            logger.info("Status to start trader websocket is false")
            return

        logger.info("Starting trader websocket")
        self._websocket = EXCHANGE_TO_WEBSOCKET[self._trader_settings.exchange](
            callback=self._message_middleware,
            connector_factory=self._connector_factory,
            user_settings=self._user_settings,
            trader_settings=self._trader_settings,
        )
        self._next_restart_time: int | float = time.time() + self._restart_interval
        self._websocket.start_websocket()

    def _restart(self) -> None:
        """ Перезапуск соединения с вебсокетом трейдера. """
        logger.info("Restarting trader websocket")
        if self._websocket:
            try:
                self._websocket.stop_websocket()
            except Exception as e:
                logger.error(f"Can not stop previous websocket connection: {e}")

        self.start()

    def _restart_thread(self) -> None:
        """ Функция перезапускает вебсокет каждые 12 часов. """
        while True:
            try:
                time.sleep(100)
                if self._next_restart_time and time.time() > self._next_restart_time:
                    self._next_restart_time: int | float = time.time() + self._restart_interval
                    self._restart()
            except Exception as e:
                logger.error(f"Error in restart thread func: {e}")

    def _message_middleware(self, *args, **kwargs) -> None:
        """ Мидлварь для принятия сообщения, в котором проводятся дополнительные проверки. """
        logger.debug(f"Websocket message: {args}, {kwargs}")
        self._last_message_time = time.time()

        if not self._check_statuses():
            logger.info("Status for processing ws message is false.")
            return

        try:
            self._websocket.handle_websocket_message(*args, **kwargs)
        except Exception as e:
            logger.error(f"Exception while handling websocket message({args=}, {kwargs=}): {e}")

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
        # User settings update always got before trader settings update, so we dont need to restart ws here.
        # self._restart()

    def on_trader_settings_update(self, u: TraderSettings) -> None:
        logger.info(f"Trader settings update event: {u}")
        self._trader_settings: TraderSettings = u
        self._restart()
