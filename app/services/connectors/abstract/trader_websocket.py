from abc import ABC, abstractmethod
from typing import Callable, Literal, Optional

from app.database import Keys
from app.schemas.models import UserSettings, TraderSettings
from .exchange_connector import AbstractExchangeConnector


class AbstractTraderWebsocket(ABC):
    """ Класс обрабатывает сообщение с вебсокета """

    def __init__(
            self,
            connector_factory: Callable[[Literal["trader", "client"]], Optional[AbstractExchangeConnector]],
            user_settings: UserSettings,
            trader_settings: TraderSettings,
    ) -> None:
        self._user_settings: UserSettings = user_settings
        self._trader_settings: TraderSettings = trader_settings
        self._connector_factory: Callable[[Literal["trader", "client"]], Optional[AbstractExchangeConnector]] = \
            connector_factory
        self._ws = None

    @abstractmethod
    def handle_websocket_message(self, msg: dict) -> None:
        """ Функция принимает и обрабатывает сообщение с вебсокета. """
        raise NotImplementedError

    @abstractmethod
    def start_websocket(self, callback: Callable[[dict], None]) -> None:
        """ Функция создает и возвращает клиент вебсокета для конкретной биржи. """
        raise NotImplementedError

    @abstractmethod
    def stop_websocket(self) -> None:
        """ Функция останавливает вебсокет. """
        raise NotImplementedError

    def __del__(self) -> None:
        try:
            self.stop_websocket()
        except:  # noqa
            pass
