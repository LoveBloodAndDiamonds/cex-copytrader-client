from binance import Client

from .abstract import AbstractExchangeConnector


class BinanceConnector(AbstractExchangeConnector):

    def __init__(self, api_key: str, api_secret: str) -> None:
        super().__init__(api_key=api_key, api_secret=api_secret)

        self._client: Client = Client(api_key=api_key, api_secret=api_secret)

    def get_current_balance(self) -> float:
        """ Returns current user balance. """
        for asset in self._client.futures_account_balance():
            if asset["asset"] == "USDT":
                return float(asset["availableBalance"])

    def on_stop_trading_event(self) -> None:
        pass
