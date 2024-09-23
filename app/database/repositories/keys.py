__all__ = ["KeysRepository", ]

from sqlalchemy.orm import sessionmaker

from ..models import Keys


class KeysRepository:
    model = Keys

    def __init__(self, session_maker: sessionmaker):
        self.session_maker = session_maker

    def get(self) -> model | None:
        """
        Возвращает модель из базы данных, если она существует.
        Если нет - то возвращает None.
        :return:
        """
        with self.session_maker() as session:
            return session.get(entity=self.model, ident=1)

    def create_if_not_exists(self) -> None:
        """
        Создает строчку с ключами в базе данных, если она еще не была создана.
        :return:
        """
        with self.session_maker() as session:
            if not session.get(entity=self.model, ident=1):
                session.add(self.model())
                session.commit()
