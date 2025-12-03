# Внешние зависимости
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
# Внутренние модули
from app.config import get_config
from app.models import DataLegislation
from app.database import connection_inner


config = get_config()


# Загружаем готовые данные
@connection_inner
async def sql_inner_add_legislation(
    legislation: DataLegislation,
    session: AsyncSession) -> bool:
    try:
        if not legislation:
            return False

        legislation_dict = legislation.to_dict()
        new_legislation = DataLegislation(**legislation_dict)
        session.add(new_legislation)

        await session.commit()
        return True

    except SQLAlchemyError as e:
        config.logger.error(f"Database error inner add legislation (id: {legislation.id}): {e}")
        return False

    except Exception as e:
        config.logger.error(f"Unexpected error inner add legislation (id: {legislation.id}): {e}")
        return False