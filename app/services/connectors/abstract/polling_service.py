from abc import ABC, abstractmethod

from app.schemas.models import UserSettings
from .exchange_connector import AbstractExchangeConnector


class AbstractPollingService(ABC):
    """
    Класс, который отвечает за сравнение ордеров и позиций клиента и трейдера.
    """

    @classmethod
    @abstractmethod
    def process(
            cls,
            client_connector: AbstractExchangeConnector,
            trader_connector: AbstractExchangeConnector,
            user_settings: UserSettings
    ) -> None:
        """ Проверка ордеров и позиций, выставление их и тд """
        raise NotImplementedError
