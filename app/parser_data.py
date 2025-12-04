# Внешние зависимости
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
# Внутренние модули
from app.crud import sql_update_legislation
from app.request import get_ready_legislation, delete_ready_legislation
from app.config import get_config
from app.database import setup_database


config = get_config()


# Парсер из готовых данных из одной бд в другую
async def parser_db():
    try:
        config.logger.info("Начало выполнения parser_db()")

        legislation_ready = await get_ready_legislation()

        while legislation_ready:
            loaded_legislation_ids = []
            for legislation in legislation_ready:
                flag_loaded = await sql_update_legislation(legislation)

                if flag_loaded:
                    loaded_legislation_ids.append(legislation["id"])

            if loaded_legislation_ids:
                await delete_ready_legislation(legislation_ids=loaded_legislation_ids)
    
            config.logger.info(f"Завершение parser_db(). Добавлено {len(loaded_legislation_ids)} записей")

            legislation_ready = await get_ready_legislation()

    except Exception as e:
        config.logger.error(f"Ошибка в parser_db(): {str(e)}")


# Запуск планировщика задач
async def start_scheduler():
    await setup_database()

    scheduler = AsyncIOScheduler()

    # Добавляем задачу, которая будет выполняться каждые 5 минут
    scheduler.add_job(
        parser_db,
        trigger=IntervalTrigger(minutes=config.PERIOD_MINUTES),
        id='parse_db_job',
        name=f'Парсинг базы данных каждые {config.PERIOD_MINUTES} минут',
        replace_existing=True,
        max_instances=1  # Не запускать параллельно, если задача еще выполняется
    )

    scheduler.start()
    config.logger.info("Планировщик APScheduler запущен")

    # Запускаем сразу первую задачу
    await parser_db()

    # Бесконечный цикл для работы планировщика
    try:
        while True:
            await asyncio.sleep(15)

    except (KeyboardInterrupt, SystemExit):
        config.logger.info("Остановка планировщика...")
        scheduler.shutdown()
        config.logger.info("Планировщик остановлен")