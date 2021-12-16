import asyncio
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData
from aiogram import Bot

from app import schedule
import app.handlers.link as link

import re
from typing import Union


callback_audit_url = CallbackData("audit_url", "verdict", "subject_id", "sender_telegram_id", "set_self")
#                                                1 | 0                                           1 | 0


class ModeratorState(StatesGroup):
    notify = State()
    set_url = State()


def _get_url(message_html_text: str) -> str:
    return re.findall(r'<a href="(.+)">посилання</a>', message_html_text)[0]


def _get_subject_name(message_html_text: str) -> str:
    return re.findall(r'<b>(.+)</b>', message_html_text)[0]


async def send_url_for_audit(message: types.Message,
                             moderator_id: Union[int, str],
                             subject_id: Union[int, str],
                             change: bool):
    """
    На підтвердження чи це посилання на цей предмет

    :param message: повідомлення з url відправлено користувачем на перевірку
    :param moderator_id: id модератога групи користувача
    :param subject_id: id предмету на яке встановлюється посилання
    :param change: чи це заміна старого посилання на нове
    """
    url = message.text.split(' ')[0]
    if change:
        online_lesson_url_and_name = schedule.get_online_lesson_url_and_name(subject_id)
        subject_name, old_url = online_lesson_url_and_name['name'], online_lesson_url_and_name['url']
    else:
        subject_name = schedule.get_subject_name(subject_id)
    text = f'Студент {message.from_user.username if message.from_user.username else message.from_user.full_name} ' \
           f'хоче встановити <a href="{url}">посилання</a> для <b>{subject_name}</b> '
    if change:
        text += f'замість <a href="{old_url}">минулого</a>'
    buttons = [
        InlineKeyboardButton(text="👍🏻", callback_data=callback_audit_url.new(
            verdict="1",
            subject_id=subject_id,
            sender_telegram_id=message.from_user.id,
            set_self="0"
        )),
        InlineKeyboardButton(text="👎🏻", callback_data=callback_audit_url.new(
            verdict="0",
            subject_id=subject_id,
            sender_telegram_id=message.from_user.id,
            set_self="0"
        ))
    ]
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    keyboard.add(InlineKeyboardButton(text=f"Ввести{' нове' if change else ''} самому✏️",
                                      callback_data=callback_audit_url.new(
                                          verdict="0",
                                          subject_id=subject_id,
                                          sender_telegram_id=message.from_user.id,
                                          set_self="1"
                                      )))
    await message.bot.send_message(moderator_id, text, reply_markup=keyboard, parse_mode='HTML',
                                   disable_web_page_preview=True)


async def verdict_url(call: types.CallbackQuery, callback_data: dict):
    url = _get_url(call.message.html_text)
    subject_name = _get_subject_name(call.message.html_text)
    verdict = bool(int(callback_data['verdict']))
    subject_id = int(callback_data["subject_id"])
    if verdict:
        schedule.add_online_lesson_url(subject_id, url)
        await call.message.edit_text("Посилання встановлено!", reply_markup=None)
    else:
        await call.message.edit_text("Посилання відхилено!", reply_markup=None)
    await reply_to_sender(call.bot, verdict, callback_data['sender_telegram_id'], subject_name, url)
    if bool(int(callback_data['set_self'])):
        await call.message.edit_text(f"Введіть посилання для <b>{subject_name}:</b>", parse_mode='HTML',
                                     reply_markup=None)
        schedule.add_wait_subject_url(call.message.chat.id, subject_id)
        await link.LinkState.set_url.set()


async def reply_to_sender(bot: Bot, verdict: bool, sender_telegram_id: Union[int, str], subject_name: str, url: str):
    await bot.send_message(sender_telegram_id,
                           f'<a href="{url}">Посилання</a> для <b>{subject_name}</b> було '
                           f'<u>{"підтверджено" if verdict else "відхилено"}!</u>',
                           parse_mode='HTML', disable_web_page_preview=True)


async def cmd_notify(message: types.Message):
    user = schedule.get_subscriber(message.from_user.id)
    if user.is_moderator:
        await message.answer(f"✏️Напиши повідомлення для <i>{user.group_name}:</i>", parse_mode='HTML')
        await ModeratorState.notify.set()


async def notify(message: types.Message, state: FSMContext):
    tasks = [asyncio.create_task(message.forward(telegram_id))
             for telegram_id in schedule.get_telegram_id_is_notification(message.from_user.id)]
    await state.finish()
    await asyncio.gather(*tasks)


def register_handlers_moderator(dp: Dispatcher):
    dp.register_callback_query_handler(verdict_url, callback_audit_url.filter(), state="*")
    dp.register_message_handler(cmd_notify, commands="notify", state="*")
    dp.register_message_handler(notify, state=ModeratorState.notify)
