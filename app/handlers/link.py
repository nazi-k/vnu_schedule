from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from random import choice

from app import schedule
from app.handlers.moderator import send_url_for_audit


class LinkState(StatesGroup):
    set_url = State()
    change_url = State()


async def answer_troll(message: types.Message):
    responses = ["Введіть посилання:\nжартую. як і ти.", "Знущаєшся з мене?", "¿?¿?", "Це ж не твій предмет!", "👀"]
    await message.answer(choice(responses))


async def non_moderator(message: types.Message):
    await message.answer("❌ Ваша група наразі не має модератора! Будь ласка, зверніться до @naz1_k!")


async def cmd_link(message: types.Message):
    subject_id = message.text.replace('/link', '').split(' ')[0]
    if subject_id.isdecimal():
        subject_id = int(subject_id)
        if schedule.is_his_subject(message.from_user.id, subject_id):
            online_lesson = schedule.get_online_lesson_url_and_name(subject_id)
            if online_lesson['url']:
                await message.answer(f'<a href="{online_lesson["url"]}">{online_lesson["name"]}</a>\n'
                                     f'✏️Введіть нове посилання:',
                                     reply_markup=types.ReplyKeyboardRemove(), parse_mode='HTML',
                                     disable_web_page_preview=True)
                await LinkState.change_url.set()
            else:
                # посилання не встановлено
                moderator_id = schedule.get_his_group_moderator(message.from_user.id)
                if moderator_id:
                    schedule.add_wait_subject_url(message.from_user.id, subject_id)
                    await message.answer(f"<b>{online_lesson['name']}\n</b>✏️Введіть посилання:",
                                         reply_markup=types.ReplyKeyboardRemove(), parse_mode='HTML')
                    await LinkState.set_url.set()
                else:
                    # модератор не встановлений
                    await non_moderator(message)
        else:
            # не його предмет
            await answer_troll(message)
    else:
        # ввів щось не те
        await answer_troll(message)


def _verification_url(url: str) -> bool:
    return url.startswith(("https://meet.google.com", "https://zoom.us", "https://astoundcommerce.zoom.us"))


async def invalid_url(message: types.Message):
    await message.answer("Не схоже на посилання заняття. Спробуй ще раз:")


async def audit_url(message: types.Message, state: FSMContext, change: bool):
    if _verification_url(message.text):
        moderator_id = schedule.get_his_group_moderator(message.from_user.id)
        if moderator_id:
            subject_id = schedule.get_wait_subject_url_subject_id(message.from_user.id)
            if moderator_id == message.from_user.id:
                schedule.add_online_lesson_url(subject_id, message.text.split(' ')[0])
                await message.answer("Посилання встановлено!")
                return
            await send_url_for_audit(message, moderator_id, subject_id, change)
            await message.answer('Посилання відправлено модератору на підтвердження.')
            await state.finish()
        else:
            await state.finish()
            await non_moderator(message)
    else:
        await invalid_url(message)


async def audit_change_url(message: types.Message, state: FSMContext):
    await audit_url(message, state, change=True)


async def audit_set_url(message: types.Message, state: FSMContext):
    await audit_url(message, state, change=False)


def register_handlers_link(dp: Dispatcher):
    dp.register_message_handler(cmd_link, Text(startswith="/link"), state="*")
    dp.register_message_handler(audit_set_url, state=LinkState.set_url)
    dp.register_message_handler(audit_change_url, state=LinkState.change_url)
