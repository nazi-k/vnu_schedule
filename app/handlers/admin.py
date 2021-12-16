from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import IDFilter, ForwardedMessageFilter
import aiogram.utils.markdown as fmt

from app import schedule
from app.daily_task import DailTask


class AdminState(StatesGroup):
    add_moderator = State()


async def moderator(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Перешліть повідомлення модератора")
    await AdminState.add_moderator.set()


async def add_moderator(message: types.Message, state: FSMContext):
    schedule.add_moderator(message.forward_from.id)
    await message.answer("Модератора добавлено!")
    await state.finish()
    await message.bot.send_message(message.forward_from.id, fmt.text(
        fmt.bold('Вітаю, тебе затверджено модератором!\n'), fmt.text('Тепер, ти можеш '),
        fmt.underline('добавляти посилання на онлайн заняття.\n'),
        fmt.text('А також, '), fmt.underline('сповіщати всю групу'), fmt.text(' /notify'), sep=''),
                                   parse_mode='MarkdownV2')


async def task(message: types.Message):
    """Точка входу виконання завдань"""
    dt = DailTask(message.bot)
    try:
        if not dt.works:
            await message.answer("Виконання завдань розпочато!")
            await dt.run()
        else:
            await message.answer("Завдання вже виконуються!")
    except Exception:
        dt.works = False
        await message.answer("Виконання завдань перервано!")


def register_hendler_admin(dp: Dispatcher, admin_id: int):
    dp.register_message_handler(moderator, IDFilter(user_id=admin_id), commands=["addm", "addmoderator"])
    dp.register_message_handler(task, IDFilter(user_id=admin_id), commands="task")
    dp.register_message_handler(add_moderator, ForwardedMessageFilter, state=AdminState.add_moderator)
