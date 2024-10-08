from typing import Optional, Literal

from binance.um_futures import UMFutures

from app.schemas.types import Order, Position
from .exchange_info import exchange_info
from ..abstract import AbstractExchangeConnector


class BinanceConnector(AbstractExchangeConnector):
    recvWindow: dict = {"recvWindow": 20000}

    def __init__(self, api_key: str, api_secret: str) -> None:
        super().__init__(api_key=api_key, api_secret=api_secret)

        self._client: UMFutures = UMFutures(key=api_key, secret=api_secret)

    def cancel_order(self, symbol: str, order_id: int | str) -> dict:
        """ Cancel order by id """
        return self._client.cancel_order(symbol=symbol, orderId=order_id)  # noqa

    def get_current_balance(self) -> float:
        """ Returns current user balance. """
        for asset in self._client.balance(**self.recvWindow):  # noqa
            if asset["asset"] == "USDT":
                return float(asset["balance"])

    def get_all_open_positions(self) -> list[dict]:
        """ Returns list of opened positions """
        result: list[Position] = []
        for p in self._client.get_position_risk(**self.recvWindow):  # noqa
            if float(p["positionAmt"]) != 0:
                result.append(p)
        return result

    def get_all_open_orders(self) -> list[dict]:
        """ Returns list of opened orders """
        return self._client.get_orders(**self.recvWindow)  # noqa

    def copy_order(self, order: Order) -> dict:
        """ Copy order from trader account """
        return self._client.new_order(
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
                callback_rate=float(order.get("priceRate", 0.0)),
                activation_price=float(order.get("activatePrice", 0.0))
            ),
            **self.recvWindow
        )

    def close_position(self, position: Position) -> dict:
        """ Close current open position """
        position_amount: float = float(position["positionAmt"])
        if position_amount == 0:
            raise ValueError(f"Trying to close position with positionAmt={position_amount}")

        return self._client.new_order(
            **self._create_order_kwargs(
                symbol=position["symbol"],
                type="MARKET",
                side="SELL" if position_amount > 0 else "BUY",
                position_side=position["positionSide"],
                quantity=position_amount,
            ),
            **self.recvWindow
        )

    def cancel_all_open_orders(self, symbol: str) -> dict:
        """ Cancel all opened orders """
        return self._client.cancel_open_orders(symbol=symbol, **self.recvWindow)  # noqa

    def cancel_order_by_client_order_id(self, symbol: str, client_order_id: str) -> dict:
        """ Cancel order by client order id """
        return self._client.cancel_order(symbol=symbol, origClientOrderId=client_order_id, **self.recvWindow)  # noqa

    def close_position_from_websocket_message(self, trader_position: dict) -> dict:
        """ Closing position after websocket message
         {'bep': '0.150465195',
          'cr': '-0.06420997',
          'ep': '0.15039',
          'iw': '0',
          'ma': 'USDT',
          'mt': 'cross',
          'pa': '113',
          'ps': 'LONG',
          's': 'TRXUSDT',
          'up': '-0.00113000'}
        """
        # position = trader position
        symbol: str = trader_position["s"]
        position_side: Literal["SHORT", "LONG"] = trader_position["ps"]

        if position_side in ["LONG", "BOTH"]:
            index: int = 0
        elif position_side == "SHORT":
            index: int = 1
        else:
            raise ValueError(f"Wrong position side: {position_side}")

        position: Position = self._client.get_position_risk(symbol=symbol, **self.recvWindow)[index]  # noqa

        return self.close_position(position=position)

    def copy_order_from_websocket_message(self, order: dict) -> dict:
        """ Copy order from trader websocket account message
        {
            "s":"BTCUSDT",			         // Symbol
            "c":"TEST",				           // Client Order Id
              // special client order id:
              // starts with "autoclose-": liquidation order
              // "adl_autoclose": ADL auto close order
              // "settlement_autoclose-": settlement order for delisting or delivery
            "S":"SELL",					         // Side
            "o":"TRAILING_STOP_MARKET",	 // Order Type
            "f":"GTC",					         // Time in Force
            "q":"0.001",				         // Original Quantity
            "p":"0",					           // Original Price
            "ap":"0",					           // Average Price
            "sp":"7103.04",				       // Stop Price. Please ignore with TRAILING_STOP_MARKET order
            "x":"NEW",					         // Execution Type
            "X":"NEW",					         // Order Status
            "i":8886774,				         // Order Id
            "l":"0",					           // Order Last Filled Quantity
            "z":"0",					           // Order Filled Accumulated Quantity
            "L":"0",					           // Last Filled Price
            "N":"USDT",            	     // Commission Asset, will not push if no commission
            "n":"0",               	     // Commission, will not push if no commission
            "T":1568879465650,			     // Order Trade Time
            "t":0,			        	       // Trade Id
            "b":"0",			    	         // Bids Notional
            "a":"9.91",					         // Ask Notional
            "m":false,					         // Is this trade the maker side?
            "R":false,					         // Is this reduce only
            "wt":"CONTRACT_PRICE", 		   // Stop Price Working Type
            "ot":"TRAILING_STOP_MARKET", // Original Order Type
            "ps":"LONG",					       // Position Side
            "cp":false,						       // If Close-All, pushed with conditional order
            "AP":"7476.89",				       // Activation Price, only puhed with TRAILING_STOP_MARKET order
            "cr":"5.0",					         // Callback Rate, only puhed with TRAILING_STOP_MARKET order
            "pP": false,                 // If price protection is turned on
            "si": 0,                     // ignore
            "ss": 0,                     // ignore
            "rp":"0",	   					       // Realized Profit of the trade
            "V":"EXPIRE_TAKER",          // STP mode
            "pm":"OPPONENT",             // Price match mode
            "gtd":0                      // TIF GTD order auto cancel time
          }
        """
        return self._client.new_order(
            **self._create_order_kwargs(
                symbol=order["s"],
                type=order["ot"],
                client_order_id=str(order["i"]),
                side=order["S"],
                position_side=order["ps"],
                price=float(order["p"]),
                quantity=float(order["q"]),
                stop_price=float(order["sp"]),
                close_position=order.get("cp", False),
            ),
            **self.recvWindow
        )

    def renew_listen_key(self, listen_key: str) -> None:
        """ Renews listen key """
        return self._client.renew_listen_key(listenKey=listen_key)  # noqa

    def create_listen_key(self) -> str:
        """ Creates listen key """
        return self._client.new_listen_key().get("listenKey")  # noqa

    def close_listen_key(self, listen_key: str) -> None:
        """ Closes listen key for user data stream """
        return self._client.close_listen_key(listenKey=listen_key)  # noqa

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
            time_in_force: Optional[str] = "GTC",
            callback_rate: Optional[float] = 0.0,
            client_order_id: Optional[str] = None,
            activation_price: Optional[float] = 0.0
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

        if type == "MARKET":
            kwargs['quantity'] = str(quantity)

        elif type == "LIMIT":
            kwargs['price'] = str(price)
            kwargs['timeInForce'] = str(time_in_force)
            kwargs['quantity'] = str(quantity)

        elif type == "STOP":
            kwargs['quantity'] = str(quantity)
            kwargs['stopPrice'] = str(stop_price)
            kwargs['price'] = str(price)

        elif type == "STOP_MARKET":
            kwargs['stopPrice'] = str(stop_price)
            kwargs['closePosition'] = str(close_position)
            kwargs['quantity'] = str(quantity)

        elif type == "TAKE_PROFIT_MARKET":
            kwargs['stopPrice'] = str(stop_price)
            kwargs['closePosition'] = str(close_position)

        elif type == "TRAILING_STOP_MARKET":
            kwargs['quantity'] = str(quantity)
            kwargs['activationPrice'] = str(activation_price)
            kwargs['callbackRate'] = str(callback_rate)

        return kwargs
