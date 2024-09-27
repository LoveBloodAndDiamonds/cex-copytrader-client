from ..abstract import AbstractExchangeConnector
from app.schemas.types import Order, Position


class MexcExchangeConnector(AbstractExchangeConnector):

    def __init__(self, api_key: str, api_secret: str) -> None:
        super().__init__(api_key, api_secret)

        self._api_key: str = api_key
        self._api_secret: str = api_secret

    def get_current_balance(self) -> float:
        """ Returns current client balance """
        raise NotImplementedError

    def get_all_open_positions(self) -> list[dict]:
        """ Returns list of opened positions """
        raise NotImplementedError

    def get_all_open_orders(self) -> list[dict]:
        """ Returns list of opened orders """
        raise NotImplementedError

    def copy_order(self, order: Order) -> dict:
        """ Copy order from trader account """
        raise NotImplementedError

    def copy_order_from_websocket_message(self, order: dict) -> dict:
        """ Copy order from trader websocket account message """
        raise NotImplementedError

    def close_position_from_websocket_message(self, position: dict) -> dict:
        """ Closing position after websocket message """
        raise NotImplementedError

    def close_position(self, position: Position) -> dict:
        """ Close current positions """
        raise NotImplementedError

    def cancel_order(self, symbol: str, order_id: int | str) -> dict:
        """ Cancel order by id """
        raise NotImplementedError

    def cancel_order_by_client_order_id(self, symbol: str, client_order_id: str) -> dict:
        """ Cancel order by client order id """
        raise NotImplementedError

    def cancel_all_open_orders(self, symbol: str) -> dict:
        """ Cancel all opened orders """
        raise NotImplementedError

