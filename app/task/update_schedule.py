from app.vnu import get_schedule
from app.schedule import add_schedule, get_all_group_name

from aiohttp import ClientSession


async def update_schedule(session: ClientSession = None):
    for group_name in get_all_group_name():
        add_schedule(await get_schedule(group_name, session=session))
