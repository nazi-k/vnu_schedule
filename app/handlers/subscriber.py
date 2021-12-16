from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import aiogram.utils.markdown as fmt
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from app import vnu, schedule, models
from app.catch_exceptions import catch_client_error


class SubscriberState(StatesGroup):
    waiting_group_name = State()
    change_group = State()


NON_GROUP = fmt.text("🔒 Вказаної групи не існує\. Спробуй ще раз\. Приклад:", fmt.italic("КНІТ-13."))


def get_keyboard_menu() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton(text="📔Розклад на сьогодні"))
    keyboard.add(KeyboardButton(text="📚Розклад на тиждень"))
    keyboard.add(KeyboardButton(text="⚙️ Налаштування"))
    return keyboard


@catch_client_error
async def set_group(message: types.Message, state: FSMContext, *args, **kwargs):  # args, kwargs для роботи Декоратора
    await group(message, state, False)


@catch_client_error
async def change_group(message: types.Message, state: FSMContext, *args, **kwargs):  # args, kwargs для Декоратора
    await group(message, state, True)


async def group(message: types.Message, state: FSMContext, change: bool):
    real_group = await vnu.get_real_group(message.text, session=message.bot.session)
    if real_group:
        if change:
            schedule.update_subscriber_group(message.from_user.id, real_group)
        else:
            schedule.add_subscriber(models.Subscriber(message.from_user.id, real_group))
        schedule.add_schedule(await vnu.get_schedule(real_group, session=message.bot.session))
        await message.answer(fmt.text(f"Групу{' змінено на' if change else ''}", fmt.underline(f"{real_group}!"),
                                      fmt.text("встановлено\!") if not change else ''),
                             parse_mode='MarkdownV2', reply_markup=get_keyboard_menu())
        await state.finish()
    else:
        await message.answer(NON_GROUP, parse_mode='MarkdownV2')


def register_handlers_subscriber(dp: Dispatcher):
    dp.register_message_handler(set_group, state=SubscriberState.waiting_group_name)
    dp.register_message_handler(change_group, state=SubscriberState.change_group)
