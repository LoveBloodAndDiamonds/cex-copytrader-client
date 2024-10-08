import json
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Literal, Optional

from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient

from app.configuration import logger
from app.schemas.models import UserSettings, TraderSettings
from ..abstract import AbstractTraderWebsocket, AbstractExchangeConnector


class BinanceTraderWebsocket(AbstractTraderWebsocket):
    """ Класс обрабатывает сообщение с вебсокета """

    def __init__(
            self,
            connector_factory: Callable[[Literal["trader", "client"]], Optional[AbstractExchangeConnector]],
            user_settings: UserSettings,
            trader_settings: TraderSettings,
            callback: Callable[[dict], None],
            max_workers: int = 5
    ) -> None:
        super().__init__(
            callback=callback,
            connector_factory=connector_factory,
            user_settings=user_settings,
            trader_settings=trader_settings
        )

        self._is_running: bool = False

        # Its important to fix connector here
        self._trader_connector: AbstractExchangeConnector = self._connector_factory("trader")

        self._executor: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=max_workers)

        self._ws: UMFuturesWebsocketClient | None = None

        self._listen_key: str | None = None

        self._positions: dict[str, dict[Literal["LONG", "SHORT", "BOTH"], dict]] = {}
        # {'TRXUSDT':
        #      {'LONG':
        #           {'bep': '0.150465195',
        #            'cr': '-0.06420997',
        #            'ep': '0.15039',
        #            'iw': '0',
        #            'ma': 'USDT',
        #            'mt': 'cross',
        #            'pa': '113',
        #            'ps': 'LONG',
        #            's': 'TRXUSDT',
        #            'up': '-0.00113000'}}}

    def start_websocket(self) -> None:
        """ Функция создает и возвращает клиент вебсокета для конкретной биржи. """
        if self._is_running:
            return  # Если вебсокет уже запущен, не перезапускаем его

        self._is_running: bool = True

        self._ws: UMFuturesWebsocketClient = UMFuturesWebsocketClient(
            on_message=self._callback,
            on_open=lambda *args: logger.info(f"Trader websocket opened: {args}"),
            on_close=lambda *args: logger.info(f"Trader websocket closed: {args}"),
            # on_ping=lambda *args: logger.debug(f"Trader websocket ping: {args}"),
            on_error=lambda *args: logger.error(f"Trader websocket error: {args}"),
            # on_pong=lambda *args: logger.debug(f"Trader websocket pong: {args}"),
        )
        self._listen_key: str = self._trader_connector.create_listen_key()
        self._ws.user_data(listen_key=self._listen_key)

        self._executor.submit(self._listen_key_renew_thread)
        self._executor.submit(self._ping_thread)

    def stop_websocket(self) -> None:
        """ Функция останавливает вебсокет. """
        self._is_running: bool = False
        try:
            if self._listen_key:
                self._trader_connector.close_listen_key(listen_key=self._listen_key)
        except Exception as e:
            logger.error(f"Error while closing listen key on stop websocket: {e}")
        self._listen_key = None
        self._ws.stop()

    def handle_websocket_message(self, *args, **kwargs) -> None:
        """ Функция принимает и обрабатывает сообщение с вебсокета. """
        msg: str = args[1]
        msg: dict = json.loads(msg)

        event_type: str = msg.get("e")
        if event_type == "ORDER_TRADE_UPDATE":
            self._executor.submit(self._order_trade_update, msg)
        elif event_type == "ACCOUNT_CONFIG_UPDATE":
            pass  # self._executor.submit(self._account_config_update, msg)
        elif event_type == "ACCOUNT_UPDATE":
            self._executor.submit(self._account_update, msg)
        else:
            logger.debug(f"Unhandled event type {event_type}: {msg}")

    def _ping_thread(self) -> None:
        """ Function pings binance.com """
        while self._is_running:
            time.sleep(60)  # every 60 sec
            try:
                if self._is_running:
                    if self._ws:
                        self._ws.ping()
            except Exception as e:
                # Error while ping: socket is already closed.
                logger.error(f"Error while ping: {e}")

    def _listen_key_renew_thread(self) -> None:
        """
        Function renews listen key
        :return:
        """
        while self._is_running:
            time.sleep(60 * 20)  # every 20 min
            try:
                if self._is_running:  # After w8ting time.sleep() flag can changed
                    if self._listen_key:
                        self._trader_connector.renew_listen_key(listen_key=self._listen_key)
                        logger.debug("Listen key renewed")
            except Exception as e:
                logger.error(f"Error while renew listen key: {e}")

    def _order_trade_update(self, msg: dict) -> None:
        """
                {
          "e":"ORDER_TRADE_UPDATE",		   // Event Type
          "E":1568879465651,			       // Event Time
          "T":1568879465650,			       // Transaction Time
          "o":{
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
        }
        """
        try:
            order: dict = msg["o"]
            order_id: str = str(order["i"])
            symbol: str = order["s"]
            order_type: str = order["o"]
            order_status: str = order["X"]
            position_side: Literal["LONG", "SHORT", "BOTH"] = order["ps"]
            # order_status_2: str = order["x"]

            # Market order need to be placed other scenario
            if order_type == "MARKET":
                if order_status == "FILLED":
                    try:
                        position: dict = self._positions[symbol][position_side]
                    except KeyError:
                        return logger.error(f"Key error while update: {msg}")
                    if float(position["pa"]) == 0:
                        logger.debug(f"Closing position after market order: {order}")
                        result: dict = self._connector_factory("client").close_position_from_websocket_message(position)
                        return logger.info(f"Closing position after market order result: {result}")
                    else:
                        logger.debug(f"Open order after market order: {order}")
                        order["q"] = float(order["q"]) * self._user_settings.multiplier
                        result: dict = self._connector_factory("client").copy_order_from_websocket_message(order)
                        return logger.info(f"Open order after market order result: {result}")

            # Limit orders / take profit orders / stop loss orders
            else:
                if order_status == "CANCELED" or order_status == "EXPIRED":
                    logger.debug(f"Canceling order {order}")
                    result: dict = self._connector_factory("client").cancel_order_by_client_order_id(
                        symbol=symbol, client_order_id=order_id)
                    return logger.info(f"Copy cancel order result: {result}")

                if order_status == "NEW":
                    logger.debug(f"Copying order {order}")
                    order["q"] = float(order["q"]) * self._user_settings.multiplier
                    result: dict = self._connector_factory("client").copy_order_from_websocket_message(order)
                    return logger.info(f"Copy order result: {result}")

        except Exception as e:
            logger.error(f"Error while _order_trade_update: {e}")

    def _account_update(self, msg: dict) -> None:
        """
        {
          "e": "ACCOUNT_UPDATE",				// Event Type
          "E": 1564745798939,            		// Event Time
          "T": 1564745798938 ,           		// Transaction
          "a":                          		// Update Data
            {
              "m":"ORDER",						// Event reason type
              "B":[                     		// Balances
                {
                  "a":"USDT",           		// Asset
                  "wb":"122624.12345678",    	// Wallet Balance
                  "cw":"100.12345678",			// Cross Wallet Balance
                  "bc":"50.12345678"			// Balance Change except PnL and Commission
                },
                {
                  "a":"BUSD",
                  "wb":"1.00000000",
                  "cw":"0.00000000",
                  "bc":"-49.12345678"
                }
              ],
              "P":[
                {
                  "s":"BTCUSDT",          	// Symbol
                  "pa":"0",               	// Position Amount
                  "ep":"0.00000",            // Entry Price
                  "bep":"0",                // breakeven price
                  "cr":"200",             	// (Pre-fee) Accumulated Realized
                  "up":"0",						// Unrealized PnL
                  "mt":"isolated",				// Margin Type
                  "iw":"0.00000000",			// Isolated Wallet (if isolated position)
                  "ps":"BOTH"					// Position Side
                }，
                {
                    "s":"BTCUSDT",
                    "pa":"20",
                    "ep":"6563.66500",
                    "bep":"0",                // breakeven price
                    "cr":"0",
                    "up":"2850.21200",
                    "mt":"isolated",
                    "iw":"13200.70726908",
                    "ps":"LONG"
                 },
                {
                    "s":"BTCUSDT",
                    "pa":"-10",
                    "ep":"6563.86000",
                    "bep":"6563.6",          // breakeven price
                    "cr":"-45.04000000",
                    "up":"-1423.15600",
                    "mt":"isolated",
                    "iw":"6570.42511771",
                    "ps":"SHORT"
                }
              ]
            }
        }
        """
        try:
            for position in msg["a"]["P"]:
                if position["s"] not in self._positions:
                    self._positions[position["s"]] = {}
                self._positions[position["s"]][position["ps"]] = position
            # from pprint import pprint
            # pprint(self._positions)
        except Exception as e:
            logger.error(f"Error while _account_update: {e}")
