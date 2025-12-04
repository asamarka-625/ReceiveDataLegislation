# Внешние зависимости
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
# Внутренние модули
from app.config import get_config
from app.models import DataLegislation
from app.database import connection


config = get_config()


# Загружаем готовые данные
@connection
async def sql_add_legislation(
    legislation_data: Dict[str, Any],
    session: AsyncSession
) -> bool:
    try:
        if not legislation_data:
            return False

        new_legislation = DataLegislation(**legislation_data)
        session.add(new_legislation)

        await session.commit()
        return True

    except SQLAlchemyError as e:
        config.logger.error(f"Database error add legislation (id: {legislation_data.get("id")}): {e}")
        return False

    except Exception as e:
        config.logger.error(f"Unexpected error add legislation (id: {legislation_data.get("id")}): {e}")
        return False