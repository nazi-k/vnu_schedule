from aiohttp.client_exceptions import ClientError
from aiogram.types import Message

from app.exceptions import NonTelegramID


def catch_non_telegram_id(func):
    async def wrapper(*args, **kwargs):
        try:
            result = await func(*args, **kwargs)
        except NonTelegramID:
            if isinstance(args[0], Message):
                await args[0].answer("🧩Для початку, мені потрібно дізнатись твою групу!\n")
        else:
            return result

    return wrapper


def catch_client_error(func):
    async def wrapper(*args, **kwargs):
        try:
            result = await func(*args, **kwargs)
        except ClientError:
            if isinstance(args[0], Message):
                await args[0].answer("🛠Сайт університету тимчасово не працює.\n"
                                     "Спробуй пізніше.")
        else:
            return result

    return wrapper
