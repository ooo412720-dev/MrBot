# app/services/scheduler.py

from apscheduler.schedulers.asyncio import (
    AsyncIOScheduler
)

from app.core.logger import logger


scheduler = AsyncIOScheduler()


async def heartbeat():

    logger.info(
        "Scheduler heartbeat"
    )


def start_scheduler():

    scheduler.add_job(

        heartbeat,

        "interval",

        minutes=5
    )

    scheduler.start()