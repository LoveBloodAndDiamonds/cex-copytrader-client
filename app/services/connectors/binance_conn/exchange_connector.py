from typing import Optional

from binance import Client
from binance.enums import *

from app.schemas.types import Order, Position
from .exchange_info import exchange_info
from ..abstract import AbstractExchangeConnector


class BinanceConnector(AbstractExchangeConnector):

    def __init__(self, api_key: str, api_secret: str) -> None:
        super().__init__(api_key=api_key, api_secret=api_secret)

        self._client: Client = Client(api_key=api_key, api_secret=api_secret)

    def cancel_order(self, symbol: str, order_id: int | str) -> dict:
        """ Cancel order by id """
        return self._client.futures_cancel_order(symbol=symbol, orderId=order_id)

    def get_current_balance(self) -> float:
        """ Returns current user balance. """
        for asset in self._client.futures_account_balance():
            if asset["asset"] == "USDT":
                return float(asset["availableBalance"])

    def get_all_open_positions(self) -> list[dict]:
        """ Returns list of opened positions """
        result: list[Position] = []
        for p in self._client.futures_position_information():
            if float(p["positionAmt"]) != 0:
                result.append(p)
        return result

    def get_all_open_orders(self) -> list[dict]:
        """ Returns list of opened orders """
        return self._client.futures_get_open_orders()

    def copy_order(self, order: Order) -> dict:
        """ Copy order from trader account """
        return self._client.futures_create_order(
            **self._create_order_kwargs(
                symbol=order["symbol"],
                type=order["type"],
                side=order["side"],
                quantity=order["origQty"],
                client_order_id=order["orderId"],
                time_in_force=order["timeInForce"],
                close_position=order["closePosition"],
                position_side=order["positionSide"],
                price=float(order["price"]),
                stop_price=float(order["stopPrice"]),
            )
        )

    def close_position(self, position: Position) -> dict:
        """ Close current open position """
        position_amount: float = float(position["positionAmt"])
        if position_amount == 0:
            raise ValueError(f"Trying to close position with positionAmt={position_amount}")

        return self._client.futures_create_order(
            **self._create_order_kwargs(
                symbol=position["symbol"],
                type=FUTURE_ORDER_TYPE_MARKET,
                side="SELL" if position_amount > 0 else "BUY",
                position_side=position["positionSide"],
                quantity=position_amount,
            )
        )

    def cancel_all_open_orders(self) -> dict:
        """ Cancel all opened orders """
        # todo we need to get all orders and set it ti symbols list
        # return self._client.futures_cancel_all_open_orders()
        pass

    def close_all_open_positions(self) -> None:
        """ Cancel all opened positions """
        pass  # todo

    def _create_order_kwargs(
            self,
            symbol: str,
            type: str,  # noqa
            side: str,
            position_side: str,
            quantity: Optional[float] = 0,
            close_position: Optional[bool] = False,
            price: Optional[float] = 0,
            stop_price: Optional[float] = 0,
            time_in_force: Optional[str] = TIME_IN_FORCE_GTC,
            callback_rate: Optional[float] = 0.0,
            client_order_id: Optional[str] = None,
    ) -> dict:
        kwargs = {
            'symbol': symbol,
            'type': type,
            'side': side,
            'positionSide': position_side
        }

        if client_order_id:
            kwargs['newClientOrderId'] = client_order_id

        # Here will be one place where price and qty rounds
        if quantity:
            quantity = abs(exchange_info.round_quantity(symbol, quantity))
        if price:
            price = exchange_info.round_price(symbol, price)
        if stop_price:
            stop_price = exchange_info.round_price(symbol, stop_price)

        if type == FUTURE_ORDER_TYPE_MARKET:
            kwargs['quantity'] = str(quantity)

        elif type == FUTURE_ORDER_TYPE_LIMIT:
            kwargs['price'] = str(price)
            kwargs['timeInForce'] = str(time_in_force)
            kwargs['quantity'] = str(quantity)

        elif type == FUTURE_ORDER_TYPE_STOP:
            kwargs['quantity'] = str(quantity)
            kwargs['stopPrice'] = str(stop_price)
            kwargs['price'] = str(price)

        elif type == FUTURE_ORDER_TYPE_STOP_MARKET:
            kwargs['stopPrice'] = str(stop_price)
            kwargs['closePosition'] = str(close_position)
            kwargs['quantity'] = str(quantity)

        elif type == FUTURE_ORDER_TYPE_TAKE_PROFIT_MARKET:
            kwargs['stopPrice'] = str(stop_price)
            kwargs['closePosition'] = str(close_position)

        elif type == FUTURE_ORDER_TYPE_TRAILING_STOP_MARKET:
            kwargs['quantity'] = str(quantity)
            kwargs['activationPrice'] = str(price)
            kwargs['callbackRate'] = str(callback_rate)

        return kwargs
