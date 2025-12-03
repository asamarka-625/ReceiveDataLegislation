# Внешние зависимости
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
# Внутренние модули
from app.crud import sql_inner_add_legislation, sql_outer_get_ready_legislation, sql_outer_delete_legislation
from app.request import post_unloaded_data
from app.config import get_config


config = get_config()


# Парсер из готовых данных из одной бд в другую
async def parser_db():
    try:
        config.logger.info("Начало выполнения parser_db()")

        legislation_ready = await sql_outer_get_ready_legislation()

        loaded_legislation_ids = []
        for legislation in legislation_ready:
            flag_loaded = await sql_inner_add_legislation(legislation)

            if flag_loaded:
                loaded_legislation_ids.append(legislation.id)

        if loaded_legislation_ids:
            await post_unloaded_data(count=len(loaded_legislation_ids))

            await sql_outer_delete_legislation(loaded_legislation_ids)

        config.logger.info(f"Завершение parser_db(). Добавлено {len(loaded_legislation_ids)} записей")

    except Exception as e:
        config.logger.error(f"Ошибка в parser_db(): {str(e)}")


# Запуск планировщика задач
async def start_scheduler():
    scheduler = AsyncIOScheduler()

    # Добавляем задачу, которая будет выполняться каждые 5 минут
    scheduler.add_job(
        parser_db,
        trigger=IntervalTrigger(minutes=5),
        id='parse_db_job',
        name='Парсинг базы данных каждые 5 минут',
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