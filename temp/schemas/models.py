from pydantic import BaseModel

from .enums import Exchange


class UserBalanceUpdate(BaseModel):
    """ Модель запроса обновления баланса от пользователя """
    ''' Значение баланса '''
    balance: int


class TraderSettings(BaseModel):
    """
    Модель настроек трейдера, которая нужна, чтобы клиент-сервер мог начать работать.
    """
    ''' Включен ли трейдер в админке '''
    status: bool

    ''' Апи ключи трейдера, чтобы клиент мог подключиться к его аккаунту по вебсокету '''
    api_key: str
    api_secret: str

    ''' К какой бирже подключен трейдер '''
    exchange: Exchange


class UserSettings(BaseModel):
    """
    Модель настороек пользователя, которая нужна чтобы клиент-сервер мог начать работать.
    """

    ''' Включен ли пользователь в админке '''
    status: bool

    ''' Порог баланса, при котором программа должна полностью выключиться '''
    balance_threshold: float

    ''' Множитель к размеру ордеров '''
    multuplier: float

