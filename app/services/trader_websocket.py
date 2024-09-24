from threading import Thread

from ..database import Keys
from ..schemas.models import UserSettings, TraderSettings


class TraderWebsocketService(Thread):

    def __init__(
            self,
            keys: Keys,
            user_settings: UserSettings,
            trader_settings: TraderSettings,
    ) -> None:
        super().__init__(daemon=True)

        self._keys: Keys = keys
        self._user_settings: UserSettings = user_settings
        self._trader_settings: TraderSettings = trader_settings

    def run(self) -> None:
        pass
