from abc import ABC, abstractmethod

from app.schemas.types import ServiceStatus


class AbstractService(ABC):

    @abstractmethod
    def get_status(self) -> ServiceStatus:
        """ Функция возвращает текущий статус сервиса. """
        raise NotImplementedError
