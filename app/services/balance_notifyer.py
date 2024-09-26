from datetime import datetime
import time

import requests

from .abstract import AbstractService
from ..configuration import config, logger
from ..schemas.exceptions import MasterServerConnectionError
from ..schemas.models import UserBalanceUpdate
from ..schemas.types import ServiceStatus


class BalanceNotifyerService(AbstractService):
    """
    Сервис, который отправляет обновление баланса на мастер-сервер.
    """

    def __init__(
            self,
            interval: int | float = config.BALANCE_NOTIFY_INTERVAL
    ) -> None:
        super().__init__()

        self._interval: int | float = interval

        self._last_notify_time: float = 0

    def get_status(self) -> ServiceStatus:
        return ServiceStatus(
            status=self._last_notify_time + 60 > time.time(),
            last_update_time=datetime.fromtimestamp(self._last_notify_time)
        )

    get_status.__doc__ = AbstractService.get_status.__doc__

    def balance_update_event(self, balance: float) -> None:
        """
        Функция отлавливает текущий баланс и отправляет его на мастер-сервер.
        :param balance:
        :return:
        """
        try:
            if self._last_notify_time + self._interval < time.time():
                self._last_notify_time: float = time.time()
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
        else:
            logger.debug(f"Balance update was sent to master-server: {response.status_code}. Balance={balance}")
