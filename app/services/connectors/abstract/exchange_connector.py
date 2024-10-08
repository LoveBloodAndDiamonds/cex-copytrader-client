from abc import ABC, abstractmethod

from app.schemas.types import Order, Position


class AbstractExchangeConnector(ABC):

    def __init__(
            self,
            api_key: str,
            api_secret: str,
    ) -> None:
        self._api_key: str = api_key
        self._api_secret: str = api_secret

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
    def copy_order(self, order: Order) -> dict:
        """ Copy order from trader account """
        raise NotImplementedError

    @abstractmethod
    def copy_order_from_websocket_message(self, order: dict) -> dict:
        """ Copy order from trader websocket account message """
        raise NotImplementedError

    @abstractmethod
    def close_position_from_websocket_message(self, position: dict) -> dict:
        """ Closing position after websocket message """
        raise NotImplementedError

    @abstractmethod
    def close_position(self, position: Position) -> dict:
        """ Close current positions """
        raise NotImplementedError

    @abstractmethod
    def cancel_order(self, symbol: str, order_id: int | str) -> dict:
        """ Cancel order by id """
        raise NotImplementedError

    @abstractmethod
    def cancel_order_by_client_order_id(self, symbol: str, client_order_id: str) -> dict:
        """ Cancel order by client order id """
        raise NotImplementedError

    @abstractmethod
    def cancel_all_open_orders(self, symbol: str) -> dict:
        """ Cancel all opened orders """
        raise NotImplementedError

    def renew_listen_key(self, listen_key: str) -> None:
        """ Renews listen key
         binance method
         """
        raise NotImplementedError

    def create_listen_key(self) -> str:
        """ Creates listen key
         binance method
         """
        raise NotImplementedError

    def close_listen_key(self, listen_key: str) -> None:
        """ Closes listen key for user data stream
         binance method
         """
        raise NotImplementedError

    # @abstractmethod
    # def open_position(self, position: Position) -> None:
    #     """ Create market order """
    #     raise NotImplementedError
    #
    # @abstractmethod
    # def create_order(self, order: Order) -> None:
    #     """ Create order """
    #     raise NotImplementedError
