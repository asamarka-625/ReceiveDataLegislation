# Внешние зависимости
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
# Внутренние модули
from app.config import get_config
from app.models import Base


# Получаем конфиг
config = get_config()

engine_outer = create_async_engine(config.DATABASE_OUTER_URL)
AsyncSessionLocalOuter = async_sessionmaker(engine_outer, expire_on_commit=False, class_=AsyncSession)

engine_inner = create_async_engine(config.DATABASE_INNER_URL)
AsyncSessionLocalInner = async_sessionmaker(engine_inner, expire_on_commit=False, class_=AsyncSession)


# Инициализируем таблицы
async def setup_database():
    config.logger.info(f"Инициализируем таблицы outer")
    async with engine_outer.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    config.logger.info(f"Инициализируем таблицы inner")
    async with engine_inner.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Декоратор подключения к внешней базе данных
def connection_outer(method):
    async def wrapper(*args, **kwargs):
        if kwargs.pop('no_decor', False):
            return await method(*args, **kwargs)

        async with AsyncSessionLocalOuter() as session:
            try:
                return await method(*args, session=session, **kwargs)

            except Exception as e:
                await session.rollback()
                raise e

            finally:
                await session.close()

    return wrapper


# Декоратор подключения к внутренней базе данных
def connection_inner(method):
    async def wrapper(*args, **kwargs):
        if kwargs.pop('no_decor', False):
            return await method(*args, **kwargs)

        async with AsyncSessionLocalInner() as session:
            try:
                return await method(*args, session=session, **kwargs)

            except Exception as e:
                await session.rollback()
                raise e

            finally:
                await session.close()

    return wrapper