from abc import ABC, abstractmethod


class AbstractAdapter(ABC):

    @classmethod
    @abstractmethod
    def adapt_positions_list(cls, positions: list) -> list:
        """ Adapt positions """
        raise NotImplementedError


    @classmethod
    @abstractmethod
    def adapt_orders_list(cls, orders: list) -> list:
        """ Adapt orders """
        raise NotImplementedError
