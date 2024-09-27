from abc import abstractmethod, ABC
from threading import Thread


class AbstractExchangeInfo(ABC, Thread):
    """
    Класс, который внутри себя обновляет информацию о том, как надо округлять
    цены монет и их количество в ордерах на разных биржах.
    """

    def __init__(self):
        Thread.__init__(self, daemon=True)

    @abstractmethod
    def run(self) -> None:
        pass

    @abstractmethod
    def round_price(self, symbol: str, price: float) -> float:
        pass

    @abstractmethod
    def round_quantity(self, symbol: str, quiantity: float) -> float:
        pass
