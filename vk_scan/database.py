from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncConnection
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.decl_api import DeclarativeMeta


class UrlConnect:
    """
    Формирование URL для подключения к СУБД
    """

    @staticmethod
    def sqllite(path_db: str):
        return f'sqlite+aiosqlite:///{path_db}'

    @staticmethod
    def postgresql(user: str, password: str, host: str, name_db: str, port: int = 5432):
        return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{name_db}"


class SQL:
    engine = AsyncEngine = None
    async_session: Any = None
    Base: DeclarativeMeta = None

    def __init__(self, url: UrlConnect):
        #: Настройки для подключения к БД
        SQL.engine = create_async_engine(url)
        #: Для Сессий
        SQL.async_session = sessionmaker(SQL.engine, class_=AsyncSession, expire_on_commit=False)
        #: Для ORM моделей
        SQL.Base = declarative_base()

    @classmethod
    def get_session_decor(cls, fun):
        """
        @get_session_dec
        async def NameFun(..., session: AsyncSession):
            await session.execute(text('''sql'''))
            # await session.commit()
        """

        async def wrapper(*arg, **kwargs):
            async with cls.async_session() as session:
                res = await fun(*arg, **kwargs, _session=session)
            return res

        return wrapper

    @classmethod
    async def get_session(cls) -> AsyncSession:
        # Получить сессию
        # Получить сессию await get_session().__anext__()
        async with cls.async_session() as session:
            yield session

    @classmethod
    async def get_session_transaction(cls) -> AsyncSession:
        # Получить сессию в транзакции
        # Получить сессию await get_session_transaction().__anext__()
        async with cls.async_session() as session:
            async with session.begin():
                yield session

    @classmethod
    async def execute_raw_sql(cls, raw_sql: str):
        """
        Выполнить сырой SQL запрос

        .. code-block:: python

            import asyncio

            schema = '''
            CREATE TABLE IF NOT EXISTS subscribe
            (
                id      serial PRIMARY KEY,
                user_id bigint unique,
                user_name VARCHAR (255)
            );
            '''

            if __name__ == '__main__':
                asyncio.run(execute_raw_sql(schema))
        """

        async with cls.engine.begin() as conn:
            await conn.execute(text(raw_sql))
            await conn.commit()

    @classmethod
    async def create_tabel(cls):
        """Создать все таблицы"""
        async with cls.engine.begin() as conn:
            conn: AsyncConnection
            await conn.run_sync(cls.Base.metadata.create_all)

    @classmethod
    async def drop_tabel(cls):
        """Удалить все таблицы"""
        # AsyncConnection
        async with cls.engine.begin() as conn:
            conn: AsyncConnection

            await conn.run_sync(cls.Base.metadata.drop_all)
