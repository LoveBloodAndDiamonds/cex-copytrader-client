from typing import Callable, Literal, Optional

from app.configuration import logger
from app.schemas.enums import Exchange
from app.schemas.models import UserSettings
from app.schemas.types import Position, Order
from app.utils import find_trader_unique_orders, find_client_unique_orders, find_unique_positions
from ..abstract import AbstractPollingService, AbstractExchangeConnector


class BinancePollingService(AbstractPollingService):
    """
    Класс, который отвечает за сравнение ордеров и позиций клиента и трейдера.
    """

    @classmethod
    def process(
            cls,
            connector_factory: Callable[[Literal["trader", "client"]], Optional[AbstractExchangeConnector]],
            user_settings: UserSettings,
    ) -> None:
        """ Проверка ордеров и позиций, выставление их и тд """
        # logger.info(f"----------------------------------------------------")

        client_connector: AbstractExchangeConnector = connector_factory("client")
        trader_connector: AbstractExchangeConnector = connector_factory("trader")

        # find positions and order for both accounts
        client_positions, trader_positions = cls._positions_finder(
            client_connector=client_connector, trader_connector=trader_connector)
        client_orders, trader_orders = cls._orders_finder(
            client_connector=client_connector, trader_connector=trader_connector)

        # if client_positions:
        #     logger.debug(f"{client_positions=}")
        # if trader_positions:
        #     logger.debug(f"{trader_positions=}")
        # if client_orders:
        #     logger.debug(f"{client_orders=}")
        # if trader_orders:
        #     logger.debug(f"{trader_orders=}")

        # find unique orders and posiitons
        client_unique_positions, trader_unique_positions = cls._unique_positions_finder(
            client_positions=client_positions,
            trader_positions=trader_positions)
        client_unique_orders, trader_unique_orders = cls._unique_orders_finder(
            client_orders=client_orders,
            trader_orders=trader_orders)

        # if client_unique_positions:
        #     logger.debug(f"{client_unique_positions=}")
        # if trader_unique_positions:
        #     logger.debug(f"{trader_unique_positions=}")
        # if client_unique_orders:
        #     logger.debug(f"{client_unique_orders=}")
        # if trader_unique_orders:
        #     logger.debug(f"{trader_unique_orders=}")

        # close client unique orders and positions
        cls._close_client_unique_positions(
            client_connector=client_connector,
            client_unique_positions=client_unique_positions)
        cls._close_client_unique_orders(
            client_connector=client_connector,
            client_unique_orders=client_unique_orders)

        # copy unique trader orders
        cls._copy_trader_orders(
            client_connector=client_connector,
            trader_unique_orders=trader_unique_orders,
            trader_positions=trader_positions,
            client_positions=client_positions,
            user_settings=user_settings
        )

    @classmethod
    def _copy_trader_orders(
            cls,
            client_connector: AbstractExchangeConnector,
            trader_unique_orders: list[Order],
            trader_positions: list[Position],
            client_positions: list[Position],
            user_settings: UserSettings
    ) -> None:
        """ Copy trader orders to client account

        По сути есть три правила у программы 2:
        - Доставить ордер если оба в позициях.
        - Не выставлять ничего если у клиента нет позиций, а у трейдера есть.
        - Если у клиента есть позиция а у трейдера нет - закрыть позицию клиента.
        - Если трейдер без позиции, но выставлена лимитка - выставить лимитку у клиента
        """
        trader_positions_t: list[tuple] = [(p["symbol"], p["positionSide"]) for p in trader_positions]
        client_positions_t: list[tuple] = [(p["symbol"], p["positionSide"]) for p in client_positions]

        for o in trader_unique_orders:
            try:
                order_t: tuple = (o["symbol"], o["positionSide"])

                # Имеют одинаковые позиции, ордер нужно открыть
                if order_t in trader_positions_t and order_t in client_positions_t:
                    o["origQty"] = float(o["origQty"]) * user_settings.multiplier
                    logger.debug(f"Both accounts in positions, place order: {o}")
                    result: dict = client_connector.copy_order(order=o)
                    logger.info(f"Order {o} copied: {result}")
                    continue

                # Позиция есть у трейдера, но нет у клиента
                if order_t in trader_positions_t and order_t not in client_positions_t:
                    logger.debug(f"Client has no position on {order_t} so order do not need to be opened: {o}")
                    continue

                # У обоих нет позиции, ордер нужно открыть
                if order_t not in trader_positions_t and order_t not in client_positions_t:
                    o["origQty"] = float(o["origQty"]) * user_settings.multiplier
                    logger.debug(f"Both accounts not in positions, place order: {o}")
                    result: dict = client_connector.copy_order(order=o)
                    logger.info(f"Order {o} copied: {result}")
                    continue

            except Exception as e:
                logger.error(f"Error while copying trader unique order({o}): {e}")

    @classmethod
    def _close_client_unique_positions(
            cls,
            client_connector: AbstractExchangeConnector,
            client_unique_positions: list[Position]
    ) -> None:
        """ Close client unique positions """
        for p in client_unique_positions:
            try:
                logger.debug(f"Close unique client position: {p}")
                result: dict = client_connector.close_position(position=p)
                logger.info(f"Position {p} closed: {result}")
            except Exception as e:
                logger.error(f"Error while closing client unique position({p}): {e}")

    @classmethod
    def _close_client_unique_orders(
            cls,
            client_connector: AbstractExchangeConnector,
            client_unique_orders: list[Order]
    ) -> None:
        """ Close client unique orders """
        for o in client_unique_orders:
            try:
                logger.debug(f"Close unique client order: {o}")
                result: dict = client_connector.cancel_order(symbol=o["symbol"], order_id=o["orderId"])
                logger.info(f"Order {o} canceled: {result}")
            except Exception as e:
                logger.error(f"Error while canceling client unique order({o}): {e}")

    @classmethod
    def _positions_finder(
            cls,
            client_connector: AbstractExchangeConnector,
            trader_connector: AbstractExchangeConnector
    ) -> tuple[list[Position], list[Position]]:
        """
        Client unique positions returned first.
        """
        client_positions: list[Position] = client_connector.get_all_open_positions()
        trader_positions: list[Position] = trader_connector.get_all_open_positions()

        return client_positions, trader_positions

    @classmethod
    def _orders_finder(
            cls,
            client_connector: AbstractExchangeConnector,
            trader_connector: AbstractExchangeConnector
    ) -> tuple[list[Order], list[Order]]:
        """
        Client orders returned first.
        """
        client_orders: list[Order] = client_connector.get_all_open_orders()
        trader_orders: list[Order] = trader_connector.get_all_open_orders()

        return client_orders, trader_orders

    @classmethod
    def _unique_positions_finder(
            cls,
            client_positions: list[Position],
            trader_positions: list[Position]
    ) -> tuple[list[Position], list[Position]]:
        """
        Client unique positions returned first.
        """
        client_unique: list[Position] = find_unique_positions(client_positions, trader_positions, Exchange.BINANCE)
        trader_unique: list[Position] = find_unique_positions(trader_positions, client_positions, Exchange.BINANCE)

        return client_unique, trader_unique

    @classmethod
    def _unique_orders_finder(
            cls,
            client_orders: list[Order],
            trader_orders: list[Order]
    ) -> tuple[list[Order], list[Order]]:
        """
        Client unique orders returned first.
        """
        client_unique: list[Order] = find_client_unique_orders(client_orders, trader_orders)  # close this
        trader_unique: list[Order] = find_trader_unique_orders(trader_orders, client_orders)  # open this

        return client_unique, trader_unique
