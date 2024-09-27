from abc import ABC, abstractmethod
from typing import Callable, Literal, Optional

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
            connector_factory: Callable[[Literal["trader", "client"]], Optional[AbstractExchangeConnector]],
            user_settings: UserSettings
    ) -> None:
        """ Проверка ордеров и позиций, выставление их и тд """
        raise NotImplementedError
