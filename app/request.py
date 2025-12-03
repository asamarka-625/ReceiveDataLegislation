# Внешние зависимости
import httpx
# Внутренние модули
from app.config import get_config


config = get_config()


# Передаем данные о выгрузке
async def post_unloaded_data(count: int) -> None:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                config.UNLOADED_DATA,
                json={
                    "count": count
                },
                timeout=30.0
            )

            if response.status_code != 200:
                config.logger.error(f"(post_unloaded_data) Ошибка запроса к контролеру: {response.status_code}")

        except httpx.RequestError as e:
            config.logger.error(f"(post_unloaded_data) Ошибка запроса к контроллеру: {str(e)}")

        except Exception as e:
            config.logger.error(f"(post_unloaded_data) Неожиданная ошибка при запросе к контроллеру : {str(e)}")
