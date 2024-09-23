from abc import ABC, abstractmethod

from app.api.models import UserSettings, TraderSettings
from app.database import Keys


class AbstractServiceManager(ABC):

    @classmethod
    @abstractmethod
    def on_user_settings_update(cls, u: UserSettings):
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def on_trader_settings_update(cls, u: TraderSettings):
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def on_api_keys_update(cls, u: Keys) -> None:
        raise NotImplementedError
