# Внешние зависимости
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, NoResultFound
import sqlalchemy as sa
# Внутренние модули
from app.config import get_config
from app.models import DataLegislation
from app.database import connection
from app.utils import get_binary_bytes


config = get_config()


# Загружаем готовые данные
@connection
async def sql_update_legislation(
    legislation_data: Dict[str, Any],
    session: AsyncSession
) -> bool:
    try:
        if not legislation_data:
            return False

        legislation_result = await session.execute(
            sa.select(DataLegislation)
            .where(DataLegislation.id == legislation_data["id"])
        )
        legislation = legislation_result.scalar_one()

        legislation.binary_pdf = get_binary_bytes(legislation_data["binary_pdf"])
        legislation.text = legislation_data["text"]

        await session.commit()
        return True

    except NoResultFound:
        config.logger.error(f"Legislation not found by id: {legislation_data['id']}")
        return False

    except SQLAlchemyError as e:
        config.logger.error(f"Database error add legislation (id: {legislation_data.get("id")}): {e}")
        return False

    except Exception as e:
        config.logger.error(f"Unexpected error add legislation (id: {legislation_data.get("id")}): {e}")
        return False