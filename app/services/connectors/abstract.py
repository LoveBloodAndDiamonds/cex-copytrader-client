from abc import ABC, abstractmethod


class AbstractExchangeConnector(ABC):

    def __init__(
            self,
            api_key: str,
            api_secret: str
    ) -> None:
        self._api_key: str = api_key
        self._api_secret: str = api_secret

    @abstractmethod
    def get_current_balance(self) -> float:
        """ Returns current client balance """
        raise NotImplementedError

    @abstractmethod
    def on_stop_trading_event(self) -> None:
        """ Cancels all open orders and close all opened positions """
        raise NotImplementedError
