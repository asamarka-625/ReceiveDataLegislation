# Внешние зависимости
import asyncio
# Внутренние модули
from app import start_scheduler


if __name__ == "__main__":
    asyncio.run(start_scheduler())