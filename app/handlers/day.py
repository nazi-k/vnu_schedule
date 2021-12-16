from aiogram import Dispatcher, types

from aiogram.utils.exceptions import MessageNotModified

from contextlib import suppress

import datetime

from app.timetable import day
from app import schedule, utils
from app.catch_exceptions import catch_client_error


@catch_client_error
async def update_day(message: types.Message, date_selected: datetime.date, *args, **kwargs):
    with suppress(MessageNotModified):
        subscriber = schedule.get_subscriber(message.chat.id)
        weekday = await schedule.get_weekday(subscriber, date_selected)
        text = day.get_day_text(weekday, subscriber, date_selected)
        keyboard = day.get_keyboard_day(date_selected)
        await message.edit_text(text, reply_markup=keyboard, parse_mode='HTML', disable_web_page_preview=True)


async def callbacks_day(call: types.CallbackQuery, callback_data: dict):
    date = callback_data["date"]
    await update_day(call.message, utils.str_to_date(date))
    await call.answer()


def register_handlers_day(dp: Dispatcher):
    dp.register_callback_query_handler(callbacks_day, day.callback_day.filter(), state="*")
