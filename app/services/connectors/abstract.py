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
        raise NotImplementedError
