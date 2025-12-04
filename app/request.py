# Внешние зависимости
from typing import List, Dict, Any
import httpx
# Внутренние модули
from app.config import get_config


config = get_config()


# Получаем данные законопроектов, которые готовы к выгрузке
async def get_ready_legislation() -> List[Dict[str, Any]]:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                config.GET_LEGISLATION_READY,
                params={
                    "limit": config.LEGISLATION_LIMIT
                },
                timeout=30.0
            )

            if response.status_code == 200:
                data = response.json()
                return data

            else:
                config.logger.error(f"(get_ready_legislation) Ошибка запроса к контролеру: {response.status_code}")
                return []

        except httpx.RequestError as e:
            config.logger.error(f"(get_ready_legislation) Ошибка запроса к контроллеру: {str(e)}")
            return []

        except Exception as e:
            config.logger.error(f"(get_ready_legislation) Неожиданная ошибка при запросе к контроллеру : {str(e)}")
            return []


# Удаляем выгруженные законопроекты
async def delete_ready_legislation(legislation_ids: List[int]) -> None:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                config.DELETE_LEGISLATION_READY,
                json={
                    "ids": legislation_ids
                },
                timeout=30.0
            )

            if response.status_code == 200:
                data = response.json()
                config.logger.info(
                    f"""Удаление выгруженных данных прошло успешно! 
                    Количество удаленных данных: {data.get("delete_count")}"""
                )

            else:
                config.logger.error(f"(delete_ready_legislation) Ошибка запроса к контролеру: {response.status_code}")

        except httpx.RequestError as e:
            config.logger.error(f"(delete_ready_legislation) Ошибка запроса к контроллеру: {str(e)}")

        except Exception as e:
            config.logger.error(f"(delete_ready_legislation) Неожиданная ошибка при запросе к контроллеру : {str(e)}")
