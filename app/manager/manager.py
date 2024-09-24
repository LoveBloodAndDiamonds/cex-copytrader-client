from ..configuration import logger
from ..database import Keys, Database
from ..services import TraderWebsocketService, BalanceUpdaterService
from ..schemas.models import UserSettings, TraderSettings
from ..utils import request_model


class ServiceManager:
    _running: bool = False
    _trader_websocket_service: TraderWebsocketService
    _balance_updater_service: BalanceUpdaterService

    @classmethod
    def run_services(cls) -> None:
        if cls._running:
            raise RuntimeError("You can not run services more than once.")
        cls._running: bool = True

        keys: Keys = Database.keys_repo.get()
        user_settings: UserSettings = request_model("user_settings", UserSettings)
        trader_settings: TraderSettings = request_model("trader_settings", TraderSettings)

        cls._trader_websocket_service: TraderWebsocketService = TraderWebsocketService(
            keys=keys,
            user_settings=user_settings,
            trader_settings=trader_settings
        )
        cls._balance_updater_service: BalanceUpdaterService = BalanceUpdaterService(
            keys=keys,
            user_settings=user_settings
        )

        cls._balance_updater_service.start()
        cls._trader_websocket_service.start()

    @classmethod
    def on_user_settings_update(cls, u: UserSettings) -> None:
        logger.info(f"User settings update: {u}")

    @classmethod
    def on_trader_settings_update(cls, u: TraderSettings) -> None:
        logger.info(f"Trader settings update: {u}")

    @classmethod
    def on_api_keys_update(cls, u: Keys) -> None:
        logger.info(f"Api keys update: {u}")
