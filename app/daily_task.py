from aiogram import Bot

import asyncio
import datetime

from app.task.tomorrow import send_tomorrow_schedule
from app.task.cleandb import clean_db
from app.task.update_schedule import update_schedule

from app.utils import today


class MetaSingleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaSingleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class DailTask(metaclass=MetaSingleton):
    works: bool = False

    def __init__(self, bot: Bot):
        self._bot = bot

    async def run(self):
        if not self.works:
            self.works = True
            while True:
                await asyncio.sleep(self._get_seconds_to(datetime.time(20, 50)))
                await update_schedule(self._bot.session)
                await asyncio.sleep(self._get_seconds_to(datetime.time(21)))
                await send_tomorrow_schedule(self._bot)
                await asyncio.sleep(self._get_seconds_to(datetime.time(3)))
                clean_db()

    @staticmethod
    def _get_seconds_to(time: datetime.time) -> float:
        this_day = today()
        if this_day.time() < time:
            next_time = datetime.datetime.combine(this_day.date(), time)
        else:
            next_time = datetime.datetime.combine(this_day.date() + datetime.timedelta(days=1), time)
        return next_time.timestamp() - this_day.timestamp()
