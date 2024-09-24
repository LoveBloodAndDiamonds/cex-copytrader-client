from abc import ABC, abstractmethod

from app.schemas.enums import Exchange
from .adapters import EXCHANGE_TO_ADAPTER, AbstractAdapter


class AbstractExchangeConnector(ABC):

    def __init__(
            self,
            api_key: str,
            api_secret: str,
            exchange: Exchange
    ) -> None:
        self._api_key: str = api_key
        self._api_secret: str = api_secret
        self._adapter: type[AbstractAdapter] = EXCHANGE_TO_ADAPTER[exchange]

    def get_all_open_positions_adapted(self) -> list:
        return self._adapter.adapt_positions_list(self.get_all_open_positions())

    def get_all_open_orders_adapted(self) -> list:
        return self._adapter.adapt_orders_list(self.get_all_open_orders())

    @abstractmethod
    def get_current_balance(self) -> float:
        """ Returns current client balance """
        raise NotImplementedError

    @abstractmethod
    def get_all_open_positions(self) -> list[dict]:
        """ Returns list of opened positions """
        raise NotImplementedError

    @abstractmethod
    def get_all_open_orders(self) -> list[dict]:
        """ Returns list of opened orders """
        raise NotImplementedError

    @abstractmethod
    def create_order(self, **params) -> None:
        """ Create order """
        raise NotImplementedError

    @abstractmethod
    def cancel_order(self, order_id: int | str) -> None:
        """ Cancel order by id """
        raise NotImplementedError

    @abstractmethod
    def cancel_all_open_orders(self) -> None:
        """ Cancel all opened orders """
        raise NotImplementedError

    @abstractmethod
    def close_all_open_positions(self) -> None:
        """ Cancel all opened positions """
        raise NotImplementedError
