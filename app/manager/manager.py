from typing import Optional

from ..configuration import logger
from ..database import Keys, Database
from ..schemas.models import UserSettings, TraderSettings
from ..services import TraderWebsocketService, BalanceUpdaterService, BalanceNotifyerService, BalanceWardenService
from ..services.connectors import AbstractExchangeConnector, EXCHANGE_TO_CONNECTOR
from ..utils import request_model


class ServiceManager:
    _running: bool = False
    _connector: Optional[AbstractExchangeConnector] = None

    _trader_websocket_service: TraderWebsocketService
    _balance_updater_service: BalanceUpdaterService
    _balance_warden_service: BalanceWardenService
    _balance_notifyer_service: BalanceNotifyerService

    @classmethod
    def run_services(cls) -> None:
        """ Функция запускает все сервисы и связывает их. """

        # Не даем запустить все сервисы второй раз
        if cls._running:
            raise RuntimeError("You can not run services more than once.")
        cls._running: bool = True

        # Получаем все текущие настройки юзера и трейдера с мастер сервера
        keys: Keys = Database.keys_repo.get()
        user_settings: UserSettings = request_model("user_settings", UserSettings)
        logger.debug(f"Got user settings from master-server: {user_settings}")
        trader_settings: TraderSettings = request_model("trader_settings", TraderSettings)
        logger.debug(f"Got trader settings from master-server: {trader_settings}")

        # Инициализируем коннектор
        cls._init_connector(keys)

        # Иницаилизируем и связываем сервисы
        cls._balance_notifyer_service = BalanceNotifyerService()
        cls._trader_websocket_service = TraderWebsocketService(
            connector_factory=cls._connector_factory,
            user_settings=user_settings,
            trader_settings=trader_settings
        )
        cls._balance_warden_service = BalanceWardenService(
            balance_threshold=user_settings.balance_threshold,
            balance_status_callback=cls._trader_websocket_service.on_balance_status_update
        )
        cls._balance_updater_service = BalanceUpdaterService(
            connector_factory=cls._connector_factory,
            balance_changed_callbacks=[
                cls._balance_notifyer_service.balance_update_event,
                cls._balance_warden_service.balance_update_event
            ]
        )

        # Запускаем сервисы
        cls._balance_updater_service.start()
        cls._trader_websocket_service.start()

    @classmethod
    def on_user_settings_update(cls, u: UserSettings) -> None:
        logger.info(f"User settings update: {u}")
        cls._balance_warden_service.update_user_settings(u)

    @classmethod
    def on_trader_settings_update(cls, u: TraderSettings) -> None:
        logger.info(f"Trader settings update: {u}")

    @classmethod
    def on_api_keys_update(cls, u: Keys) -> None:
        logger.info(f"Api keys update: {u}")
        cls._init_connector(u)

    @classmethod
    def _init_connector(cls, keys: Keys) -> None:
        """ Функция обновляет коннектор. """
        try:
            if keys.is_fully_filled():
                cls._connector = EXCHANGE_TO_CONNECTOR[keys.exchange](
                    api_key=keys.api_key,
                    api_secret=keys.api_secret)
                logger.debug(f"Connector updated")
            else:
                cls._connector = None
                logger.info(f"Keys model is not fully filled, can't init connector")
        except Exception as e:
            cls._connector = None
            logger.error(f"Error while init connector: {e}")

    @classmethod
    def _connector_factory(cls) -> AbstractExchangeConnector:
        """
        Функция передается как фабрика коннектора, при обновлении коннектора, нужно будет единожды обновлять его тут,
        и он автоматически должен подтягиваться в другие классы.
        :return:
        """
        return cls._connector
