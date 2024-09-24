from threading import Thread

from ..database import Keys
from ..schemas.models import UserSettings, TraderSettings
from ..configuration import logger


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

    def run(self) -> None:
        pass

    def stop_trade_event(self) -> None:
        logger.warning("stop trade event")

    def start_trade_event(self) -> None:
        logger.warning("start trade event")

    def on_user_settings_update(self, u: UserSettings) -> None:
        logger.warning("user settings update event")
        # make something about status

    def on_trader_settings_update(self, u: TraderSettings) -> None:
        logger.warning("trader settings update event")
        # make something about status
