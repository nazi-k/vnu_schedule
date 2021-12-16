from aiogram import Dispatcher, types
from aiogram.utils.exceptions import MessageNotModified
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData
from contextlib import suppress

from typing import Optional

from app import schedule
from app.models import Subscriber


callback_settings = CallbackData("settings", "key", "value")
# "subgroup", "reminder", "show_online_link", "notification_from_moderator"


def _get_subgroup(subgroup: Optional[int]) -> str:
    if subgroup == 1:
        return "перша"
    if subgroup == 2:
        return "друга"
    else:
        return "загальна"


def get_keyboard_settings(subscriber: Subscriber) -> InlineKeyboardMarkup:

    buttons_subgroup = [
        InlineKeyboardButton(text=f"{'▶️' if subscriber.subgroup == 1 else ''}l група",
                             callback_data=callback_settings.new(key="subgroup", value="1")),

        InlineKeyboardButton(text=f"{'▶️' if not subscriber.subgroup else ''}Обидві",
                             callback_data=callback_settings.new(key="subgroup", value="0")),

        InlineKeyboardButton(text=f"{'▶️' if subscriber.subgroup == 2 else ''}ll група",
                             callback_data=callback_settings.new(key="subgroup", value="2"))
    ]

    button_reminder_time = InlineKeyboardButton(
        text=f"Розклад на завтра{'✅️' if subscriber.reminder else '❎'}",
        callback_data=callback_settings.new(key="reminder",
                                            value=f"{'0' if subscriber.reminder else '1'}")
    )
    buttons_show_online_link = InlineKeyboardButton(
        text=f"Онлайн заняття{'✅️' if subscriber.show_online_link else '❎'}",
        callback_data=callback_settings.new(key="show_online_link",
                                            value=f"{'0' if subscriber.show_online_link else '1'}")
    )
    buttons_notification_from_moderator = InlineKeyboardButton(
        text=f"Сповіщення модератора{'🔔' if subscriber.notification_from_moderator else '🔕'}",
        callback_data=callback_settings.new(key="notification_from_moderator",
                                            value=f"{'0' if subscriber.notification_from_moderator else '1'}")
    )
    keyboard = InlineKeyboardMarkup(row_width=3)
    keyboard.add(*buttons_subgroup)
    keyboard.add(button_reminder_time)
    keyboard.add(buttons_show_online_link)
    keyboard.add(buttons_notification_from_moderator)
    return keyboard


def get_settings_text(subscriber: Subscriber) -> str:
    """Використовувати parse_mode='HTML'"""
    return f"⚙️ <b>Налаштування:</b>\n\n" \
           f"📚 <b>Група:</b> {subscriber.group_name}\n" \
           f"👨🏻‍🎓 <b>Підгрупа:</b> {_get_subgroup(subscriber.subgroup)}\n" \
           f"⏰ <b>Нагадування:</b> {'ввімкнене' if subscriber.reminder else 'вимкнене'}\n" \
           f"🖇 <b>Посилання на онлайн заняття:</b> {'показувати' if subscriber.show_online_link else 'приховати'}\n" \
           f"🛎️ <b>Сповіщення від модератора:</b> {'не ' if not subscriber.notification_from_moderator else ''}отримувати"


async def update_settings(message: types.Message):
    with suppress(MessageNotModified):
        subscriber = schedule.get_subscriber(message.chat.id)
        await message.edit_text(get_settings_text(subscriber),
                                reply_markup=get_keyboard_settings(subscriber),
                                parse_mode='HTML')


async def callbacks_settings(call: types.CallbackQuery, callback_data: dict):
    new_settings = {callback_data["key"]: callback_data["value"]}
    schedule.set_subscriber_settings(call.message.chat.id, new_settings)
    await update_settings(call.message)
    await call.answer()


def register_handlers_settings(dp: Dispatcher):
    dp.register_callback_query_handler(callbacks_settings, callback_settings.filter(), state="*")
