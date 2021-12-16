from aiogram import Dispatcher, types

from aiogram.utils.exceptions import MessageNotModified

from contextlib import suppress

import datetime

from app.timetable import week, day
from app import schedule, utils
from app.catch_exceptions import catch_client_error


@catch_client_error
async def update_week(message: types.Message, monday_selected: datetime.date, selected_day: int, *args, **kwargs):
    with suppress(MessageNotModified):
        subscriber = schedule.get_subscriber(message.chat.id)
        date_selected = monday_selected + datetime.timedelta(days=int(selected_day))
        weekday = await schedule.get_weekday(subscriber, date_selected)
        week_message = day.get_day_text(weekday, subscriber, date_selected)
        await message.edit_text(week_message, reply_markup=week.get_keyboard_week(monday_selected, selected_day),
                                parse_mode='HTML',
                                disable_web_page_preview=True)


async def callbacks_week(call: types.CallbackQuery, callback_data: dict):
    monday_date = callback_data["monday_date"]
    selected_day = callback_data["selected_day"]
    await update_week(call.message, utils.str_to_date(monday_date), selected_day)
    await call.answer()


def register_handlers_week(dp: Dispatcher):
    dp.register_callback_query_handler(callbacks_week, week.callback_week.filter(), state="*")
