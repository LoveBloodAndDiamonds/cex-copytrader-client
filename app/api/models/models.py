from pydantic import BaseModel

from app.database import Exchange


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

    def __str__(self) -> str:
        return (f"TraderSettings(status={self.status}, api_key={'*' * len(self.api_key)},"
                f" api_secret={'*' * len(self.api_secret)}, exchange={self.exchange})")

    def __repr__(self) -> str:
        return (f"<TraderSettings (status={self.status}, api_key={'*' * len(self.api_key)},"
                f" api_secret={'*' * len(self.api_secret)}, exchange={self.exchange})>")


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

    def __str__(self) -> str:
        return (f"UserSettings(status={self.status}, balance_threshold={self.balance_threshold},"
                f" multuplier={self.multuplier})")

    def __repr__(self) -> str:
        return (f"<UserSettings(status={self.status}, balance_threshold={self.balance_threshold},"
                f" multuplier={self.multuplier})>")
