from pydantic import BaseModel

from .enums import Exchange


class UserBalanceUpdate(BaseModel):
    """ Модель запроса обновления баланса от пользователя """
    ''' Значение баланса '''
    balance: float


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

    def __str__(self) -> str:
        return (f"TraderSettings(status={self.status}, api_key_len={len(self.api_key or '')},"
                f" api_secret_len={len(self.api_secret or '')}, exchange={self.exchange})")

    def __repr__(self) -> str:
        return (f"<TraderSettings (status={self.status}, api_key_len={len(self.api_key or '')},"
                f" api_secret_len={len(self.api_secret or '')}, exchange={self.exchange})>")

    def is_fully_filled(self) -> bool:
        return all([self.api_key, self.api_secret, self.exchange])


class UserSettings(BaseModel):
    """
    Модель настороек пользователя, которая нужна чтобы клиент-сервер мог начать работать.
    """

    ''' Включен ли пользователь в админке '''
    status: bool

    ''' Порог баланса, при котором программа должна полностью выключиться '''
    balance_threshold: float

    ''' Множитель к размеру ордеров '''
    multiplier: float

    def __str__(self) -> str:
        return (f"UserSettings(status={self.status}, balance_threshold={self.balance_threshold},"
                f" multiplier={self.multiplier})")

    def __repr__(self) -> str:
        return (f"<UserSettings(status={self.status}, balance_threshold={self.balance_threshold},"
                f" multiplier={self.multiplier})>")
