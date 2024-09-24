from .abstract import AbstractAdapter


class BinanceAdapter(AbstractAdapter):

    @classmethod
    def adapt_positions_list(cls, positions: list) -> list:
        return positions

    @classmethod
    def adapt_orders_list(cls, orders: list) -> list:
        """ Adapt orders """
        return orders
