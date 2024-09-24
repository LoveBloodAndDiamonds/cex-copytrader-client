from threading import Thread

from ..configuration import logger
from ..schemas.enums import BalanceStatus
from ..schemas.models import UserSettings, TraderSettings


class TraderWebsocketService(Thread):

    def __init__(
            self,
            connector_factory: callable,
            user_settings: UserSettings,
            trader_settings: TraderSettings,
    ) -> None:
        super().__init__(daemon=True)

        self._connector_factory: callable = connector_factory
        self._user_settings: UserSettings = user_settings
        self._trader_settings: TraderSettings = trader_settings
        self._balance_status: BalanceStatus = BalanceStatus.NOT_DEFINED

    def run(self) -> None:
        # then connector is none - we need to stop trading also
        pass

    def _websocket_callback_handler(self, msg: dict) -> None:
        if not self._connector_factory:
            pass
        if not self._user_settings.status:
            pass
        if not self._trader_settings.status:
            pass
        if self._balance_status != BalanceStatus.CAN_TRADE:
            pass

    def on_balance_status_update(self, balance_status: BalanceStatus):
        logger.warning(f"Balance status update: {balance_status}")
        self._balance_status = balance_status

    def on_user_settings_update(self, u: UserSettings) -> None:
        logger.warning(f"User settings update event: {u}")
        self._user_settings: UserSettings = u

    def on_trader_settings_update(self, u: TraderSettings) -> None:
        logger.warning(f"Trader settings update event: {u}")
        self._trader_settings: TraderSettings = u
