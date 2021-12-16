import random

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
import aiogram.utils.markdown as fmt

from app import schedule
from app.handlers.subscriber import SubscriberState
from app.timetable import day, week
from app.utils import today, get_week_monday

from app.handlers import settings
from app.catch_exceptions import catch_client_error, catch_non_telegram_id


HELP_MESSAGE = """<b>Команди:
   [ Власні налаштування ]</b>
   /settings - сповіщення і відображення розкладу
   /change_group - перейти в іншу групу

   <b>[ Розклад ]</b>
   /week - по днях тижня
   /day - по даті дня"""

START_MASSAGE = f"""
<b>Вітаю тебе в помічнику нового покоління!</b>

Більше не потрібно використовувати незрозумілий сайт, щоб дізнатись, чи є завтра пари.

{HELP_MESSAGE}

Ти - староста?
Повідом про це @naz1_k та отримай привілеї.

Оригінальний розклад було завантажено з http://194.44.187.20/cgi-bin/timetable.cgi?n=700
Фідбек: @naz1_k"""


GROUP_MASSAGE = fmt.text("✏️Відправ назву групи, наприклад,", fmt.italic("КНІТ-13"))


async def cmd_start(message: types.Message, state: FSMContext):
    if schedule.is_subscriber(message.from_user.id):
        responses = ["Що як?", "Як тебе досі не відрахували?", "/start",
                     "Не можна повернутися в минуле і змінити свій старт, "
                     "але можна стартувати зараз і змінити свій фініш.",
                     f"Залишилось спроб: {random.randint(1, 100)}", "finish\\"]
        await message.answer(random.choice(responses))
        return
    await state.finish()
    await message.answer(START_MASSAGE, parse_mode='HTML')
    await message.answer(GROUP_MASSAGE, parse_mode='MarkdownV2')
    await SubscriberState.waiting_group_name.set()


@catch_non_telegram_id
async def cmd_settings(message: types.Message, *args, **kwargs):
    subscriber = schedule.get_subscriber(message.from_user.id)
    await message.answer(settings.get_settings_text(subscriber),
                         reply_markup=settings.get_keyboard_settings(subscriber),
                         parse_mode='HTML')


@catch_non_telegram_id
@catch_client_error
async def cmd_day(message: types.Message, *args, **kwargs):  # args, kwargs для роботи Декоратора
    subscriber = schedule.get_subscriber(message.from_user.id)
    weekday = await schedule.get_weekday(subscriber)
    date_selected = today()
    text = day.get_day_text(weekday, subscriber, date_selected)
    keyboard = day.get_keyboard_day(date_selected)
    await message.answer(text, reply_markup=keyboard, parse_mode='HTML', disable_web_page_preview=True)


@catch_non_telegram_id
@catch_client_error
async def cmd_week(message: types.Message, *args, **kwargs):  # args, kwargs для роботи Декоратора
    subscriber = schedule.get_subscriber(message.from_user.id)
    selected_day = today().date()
    weekday = await schedule.get_weekday(subscriber, selected_day)
    week_message = day.get_day_text(weekday, subscriber, selected_day)
    await message.answer(week_message, reply_markup=week.get_keyboard_week(get_week_monday(), selected_day.weekday()),
                         parse_mode='HTML',
                         disable_web_page_preview=True)


async def cmd_help(message: types.Message):
    help_message = HELP_MESSAGE
    if schedule.is_moderator(message.from_user.id):
        help_message += f"\n\n" \
                        f"   <b>[ Модерація ]</b>\n" \
                        f"   /notify - сповістити групу"
    await message.answer(help_message, parse_mode='HTML')


async def cmd_change_group(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(GROUP_MASSAGE, parse_mode='MarkdownV2', reply_markup=types.ReplyKeyboardRemove())
    if not schedule.is_subscriber(message.from_user.id):
        await SubscriberState.waiting_group_name.set()
    else:
        await SubscriberState.change_group.set()


def register_handlers_cmd(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands="start", state="*")
    dp.register_message_handler(cmd_settings, commands="settings", state="*")
    dp.register_message_handler(cmd_help, commands="help", state="*")
    dp.register_message_handler(cmd_week, commands="week", state="*")
    dp.register_message_handler(cmd_day, commands="day", state="*")
    dp.register_message_handler(cmd_change_group, commands="change_group", state="*")
    dp.register_message_handler(cmd_day, Text(equals="📔Розклад на сьогодні"), state="*")
    dp.register_message_handler(cmd_week, Text(equals="📚Розклад на тиждень"), state="*")
    dp.register_message_handler(cmd_settings, Text(equals="⚙️ Налаштування"), state="*")
