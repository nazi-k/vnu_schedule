from aiogram import Bot

import asyncio
import datetime

from app.models import Subscriber, WeekDay
from app.utils import get_weekday_name, today
from app.schedule import get_subscribers_is_reminder, get_weekday
from app.timetable.day import build_day


def get_text(day: WeekDay, subscriber: Subscriber) -> str:
    return f"Твій розклад на завтра ({get_weekday_name(day.date)})\n\n" + build_day(day, subscriber)


async def get_tomorrow_day(subscriber: Subscriber) -> WeekDay:
    return await get_weekday(subscriber, (today() + datetime.timedelta(days=1)).date())


async def send_tomorrow_schedule(bot: Bot):
    subscribers = get_subscribers_is_reminder()
    tasks = []
    for subscriber in subscribers:
        day = await get_tomorrow_day(subscriber)
        if day.lessons:
            tasks.append(asyncio.create_task(bot.send_message(subscriber.telegram_id, get_text(day, subscriber),
                                                              parse_mode='HTML', disable_web_page_preview=True)))
    await asyncio.gather(*tasks)
