from typing import Optional, Literal

from ..configuration import logger
from ..database import Keys, Database
from ..schemas.models import UserSettings, TraderSettings
from ..utils import request_model
from ..services import *


class ServiceManager:
    _running: bool = False
    _client_connector: Optional[AbstractExchangeConnector] = None
    _trader_connector: Optional[AbstractExchangeConnector] = None

    _trader_websocket_service: TraderWebsocketService
    _trader_polling_service: TraderPollingService
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

        # Инициализируем коннекторы
        cls._init_client_connector(keys)
        cls._init_trader_connector(trader_settings)

        # Иницаилизируем и связываем сервисы
        cls._balance_notifyer_service = BalanceNotifyerService()
        cls._trader_polling_service = TraderPollingService(
            connector_factory=cls._connector_factory,
            user_settings=user_settings,
            trader_settings=trader_settings
        )
        cls._trader_websocket_service = TraderWebsocketService(
            connector_factory=cls._connector_factory,
            user_settings=user_settings,
            trader_settings=trader_settings
        )
        cls._balance_warden_service = BalanceWardenService(
            connector_factory=cls._connector_factory,
            balance_threshold=user_settings.balance_threshold,
            balance_status_callbacks=[
                cls._trader_websocket_service.on_balance_status_update,
                cls._trader_polling_service.on_balance_status_update
            ]
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
        cls._trader_polling_service.start()
        cls._trader_websocket_service.start()

    @classmethod
    def on_user_settings_update(cls, u: UserSettings) -> None:
        logger.info(f"User settings update: {u}")
        cls._balance_warden_service.on_user_settings_update(u)
        cls._trader_websocket_service.on_user_settings_update(u)

    @classmethod
    def on_trader_settings_update(cls, u: TraderSettings) -> None:
        logger.info(f"Trader settings update: {u}")
        cls._trader_websocket_service.on_trader_settings_update(u)
        cls._init_trader_connector(u)

    @classmethod
    def on_api_keys_update(cls, u: Keys) -> None:
        logger.info(f"Api keys update: {u}")
        cls._init_client_connector(u)

    @classmethod
    def _init_client_connector(cls, keys: Keys) -> None:
        """ Функция обновляет коннектор. """
        try:
            if keys.is_fully_filled():
                cls._client_connector = EXCHANGE_TO_CONNECTOR[keys.exchange](
                    api_key=keys.api_key,
                    api_secret=keys.api_secret,
                )
                logger.debug(f"Connector updated")
            else:
                cls._client_connector = None
                logger.info(f"Keys model is not fully filled, can't init connector")
        except Exception as e:
            cls._client_connector = None
            logger.error(f"Error while init connector: {e}")

    @classmethod
    def _init_trader_connector(cls, trader_settings: TraderSettings) -> None:
        """ Функция обновляет коннектор трейдера. """
        try:
            if trader_settings.is_fully_filled():
                cls._trader_connector = EXCHANGE_TO_CONNECTOR[trader_settings.exchange](
                    api_key=trader_settings.api_key,
                    api_secret=trader_settings.api_secret,
                )
                logger.debug(f"Trader connector updated")
            else:
                cls._trader_connector = None
                logger.info(f"Trader settings model is not fully filled, can't init trader connector")
        except Exception as e:
            cls._trader_connector = None
            logger.error(f"Error while init trader connector: {e}")

    @classmethod
    def _connector_factory(cls, which: Literal["trader", "client"]) -> AbstractExchangeConnector:
        """
        Функция передается как фабрика коннектора, при обновлении коннектора, нужно будет единожды обновлять его тут,
        и он автоматически будет подтягиваться в другие классы.
        :return:
        """
        if which == "client":
            return cls._client_connector
        elif which == "trader":
            return cls._trader_connector
        else:
            raise ValueError("Wrong connector type!")
