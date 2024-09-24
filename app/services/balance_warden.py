from typing import Callable

from ..configuration import logger
from ..schemas.models import UserSettings
from ..schemas.enums import BalanceStatus


class BalanceWardenService:
    """
    Класс проверяет текущий баланс пользователя с порогом баланса для отключения торговли.
    """

    def __init__(
            self,
            balance_threshold: float,
            balance_status_callback: Callable[[BalanceStatus], None],
    ) -> None:
        """
        :param balance_threshold: Настройки пользователя
        """
        self._balance_threshold: float = balance_threshold
        self._balance_status_callback: Callable[[BalanceStatus], None] = balance_status_callback

        # Используется чтобы не вызывать функции много раз попусту
        self._balance_status: BalanceStatus = BalanceStatus.NOT_DEFINED

    def balance_update_event(self, balance: float) -> None:
        """ Функция принимает текущий баланс пользователя и сравнивает его с порогом баланса. """
        try:
            if balance < self._balance_threshold and self._balance_status != BalanceStatus.CANT_TRADE:
                logger.critical(f"Current balance({balance}) lower than balance threshold({self._balance_threshold})!")
                self._balance_status: BalanceStatus = BalanceStatus.CANT_TRADE
                self._balance_status_callback(self._balance_status)
            elif balance > self._balance_threshold and self._balance_status != BalanceStatus.CAN_TRADE:
                logger.success(f"Current balance({balance}) greater than balance threshold({self._balance_threshold})!")
                self._balance_status: BalanceStatus = BalanceStatus.CAN_TRADE
                self._balance_status_callback(self._balance_status)
        except Exception as e:
            logger.error(f"Error while warden client balance: {e}")

    def update_user_settings(self, user_settings: UserSettings) -> None:
        """ Функция обновляет порог баланса. """
        self._balance_status: BalanceStatus = BalanceStatus.NOT_DEFINED
        self._balance_threshold: float = user_settings.balance_threshold
