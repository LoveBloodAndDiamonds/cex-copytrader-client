from sqlalchemy.orm import Mapped, mapped_column

from app.schemas.enums import Exchange
from .base import Base


class Keys(Base):
    """ Database keys model """

    __tablename__ = "keys_table"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True, nullable=False, autoincrement=True)

    exchange: Mapped[Exchange] = mapped_column(nullable=True, unique=True)

    api_key: Mapped[str] = mapped_column(nullable=True, unique=True)

    api_secret: Mapped[str] = mapped_column(nullable=True, unique=True)

    def __str__(self) -> str:
        return (f"KeysORM(id={self.id}, exchange={self.exchange or ''}, api_key_len={len(self.api_key or '')}, "
                f"api_secret_len={len(self.api_secret or '')})")

    def __repr__(self) -> str:
        return (f"<KeysORM(id={self.id}, exchange={self.exchange or ''}, api_key_len={len(self.api_key or '')}, "
                f"api_secret_len={len(self.api_secret or '')})>")

    def is_fully_filled(self) -> bool:
        return all([self.api_key, self.api_secret, self.exchange])
