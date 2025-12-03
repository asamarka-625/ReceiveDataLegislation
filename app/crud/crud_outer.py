# Внешние зависимости
from typing import List
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
# Внутренние модули
from app.config import get_config
from app.models import DataLegislation
from app.database import connection_outer


config = get_config()


# Берем готовые к выгрузке данные
@connection_outer
async def sql_outer_get_ready_legislation(limit: int, session: AsyncSession) -> List[DataLegislation]:
    try:
        legislation_result = await session.execute(
            sa.select(DataLegislation)
            .where(
                DataLegislation.binary_pdf != None,
                DataLegislation.text != None
            )
            .limit(limit)
        )
        legislation = legislation_result.scalars().all()

        return legislation

    except SQLAlchemyError as e:
        config.logger.error(f"Database error outer reading ready legislation: {e}")

    except Exception as e:
        config.logger.error(f"Unexpected error outer reading ready legislation: {e}")


# Удаляем данные
@connection_outer
async def sql_outer_delete_legislation(
    legislation_ids: List[int],
    session: AsyncSession
) -> None:
    try:
        await session.execute(
            sa.delete(DataLegislation)
            .where(DataLegislation.id.in_(legislation_ids))
        )
        await session.commit()

    except SQLAlchemyError as e:
        config.logger.error(f"Database error outer delete legislation: {e}")

    except Exception as e:
        config.logger.error(f"Unexpected error outer delete legislation: {e}")