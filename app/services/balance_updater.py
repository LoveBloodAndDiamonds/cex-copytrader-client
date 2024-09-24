from typing import Optional

import requests
from threading import Thread
import time

from .connectors import EXCHANGE_TO_CONNECTOR, AbstractExchangeConnector
from ..database import Keys
from ..schemas.models import UserSettings, UserBalanceUpdate
from ..schemas.exceptions import MasterServerConnectionError
from ..configuration import config, logger


class BalanceUpdaterService(Thread):

    def __init__(
            self,
            keys: Keys,
            user_settings: UserSettings,
            interval: int | float = config.BALANCE_UPDATE_INTERVAL
    ) -> None:
        """
        :param keys: Модель ключей из базы данных.
        :param user_settings: Модель настроек пользователя с мастер-сервера.
        """
        super().__init__(daemon=True)

        self._keys: Keys = keys
        self._user_settings: UserSettings = user_settings

        self._interval: int | float = interval

        self._connector: Optional[AbstractExchangeConnector] = None
        self.init_connector()

        self._master_server_notifyer: MasterServerNotifyer = MasterServerNotifyer()
        self._client_balance_warden: ClientBalanceWarden = ClientBalanceWarden()

    def init_connector(self) -> None:
        """ Функция обновляет коннектор. """
        try:
            if self._keys.is_fully_filled():
                self._connector = EXCHANGE_TO_CONNECTOR[self._keys.exchange](
                    api_key=self._keys.api_key,
                    api_secret=self._keys.api_secret)
            else:
                self._connector = None
                logger.debug(f"Keys model is not fully filled, can't init connector")
        except Exception as e:
            self._connector = None
            logger.error(f"Error while init connector: {e}")

    def run(self) -> None:
        """ Точка запуска сервиса. """
        while True:
            try:
                if self._connector:
                    balance: float = self._connector.get_current_balance()
                    self._master_server_notifyer.handle_balance_update(balance=balance)
                pass
            except Exception as e:
                logger.error(f"Error while update balance: {e}")
            finally:
                time.sleep(self._interval)

    def update_keys(self, keys: Keys) -> None:
        """ Функция обновляет ключи для сервиса """
        self._keys: Keys = keys
        self.init_connector()

    def update_user_settings(self, user_settings: UserSettings) -> None:
        """ Функция обновляет настройки пользователя для сервиса """
        self._user_settings: UserSettings = user_settings


class MasterServerNotifyer:
    """
    Сервис, который отправляет обновление баланса на мастер-сервер.
    """

    def __init__(
            self,
            interval: int | float = config.BALANCE_NOTIFY_INTERVAL
    ) -> None:
        self._interval: int | float = interval

        self._last_notify_time: float = 0

    def handle_balance_update(self, balance: float) -> None:
        """
        Функция отлавливает текущий баланс и отправляет его на мастер-сервер.
        :param balance:
        :return:
        """
        try:
            if self._last_notify_time + self._interval < time.time():
                self._send_notify(balance=balance)
        except Exception as e:
            logger.error(f"Error while notify master-server about balance: {e}")

    def _send_notify(self, balance: float, endpoint: str = "balance") -> None:
        """
        Function sends request to master server to update current user balance.
        :param balance: Current user balance
        :param endpoint: Endpoint to update balance
        :return: None
        """
        response: requests.Response = requests.post(
            url=f"http://{config.MASTER_SERVER_HOST}:{config.MASTER_SERVER_PORT}/{endpoint}",
            data=UserBalanceUpdate(balance=balance).model_dump_json())

        if response.status_code != 200:
            raise MasterServerConnectionError(status_code=response.status_code, response_text=response.text)


class ClientBalanceWarden:
    def __init__(self) -> None:
        pass

    def handle_balance_update(self, balance: float) -> None:
        try:
            pass
        except Exception as e:
            logger.error(f"Error while warden client balance: {e}")
