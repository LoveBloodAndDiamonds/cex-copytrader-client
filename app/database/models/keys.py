from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from ..schemas import Exchange


class Keys(Base):
    """ Database keys model """

    __tablename__ = "keys_table"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True, nullable=False, autoincrement=True)

    exchange: Mapped[Exchange] = mapped_column(nullable=True, unique=True)

    api_key: Mapped[str] = mapped_column(nullable=True, unique=True)

    api_secret: Mapped[str] = mapped_column(nullable=True, unique=True)
