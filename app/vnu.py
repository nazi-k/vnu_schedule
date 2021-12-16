import aiohttp
from typing import Union, Optional
import datetime


from urllib.parse import quote

from app.models import Group, Schedule
import app.utils as utils
import app.parser as parser

from json.decoder import JSONDecodeError

URL = "http://194.44.187.20/cgi-bin/timetable.cgi"


async def get_schedule(group: Union[str, Group],
                       start_date: Optional[datetime.date] = None,
                       end_date: Optional[datetime.date] = None,
                       session: Optional[aiohttp.ClientSession] = None) -> Schedule:
    if session:
        return await _get_schedule(group, session, start_date, end_date)
    async with aiohttp.ClientSession() as session:
        return await _get_schedule(group, session, start_date, end_date)


async def _get_schedule(group: Union[str, Group],
                        session: aiohttp.ClientSession,
                        start_date: Optional[datetime.date] = None,
                        end_date: Optional[datetime.date] = None) -> Schedule:
    if not start_date:
        start_date = utils.get_week_monday()
    if not end_date:
        end_date = start_date + datetime.timedelta(days=13)

    data = f"faculty=0&teacher=&group={quote(str(group), encoding='Windows 1251')}" \
           f"&sdate={utils.get_d_m_y(start_date)}&edate={utils.get_d_m_y(end_date)}&n=700"

    async with session.post(url=URL + "?n=700", data=data) as schedule_response:
        return parser.get_schedule(await schedule_response.text())


async def get_week_schedule(group: Union[str, Group],
                            monday: Optional[datetime.date] = utils.get_week_monday(),
                            session: Optional[aiohttp.ClientSession] = None):
    if session:
        return await _get_week_schedule(group, session, monday)
    async with aiohttp.ClientSession() as session:
        return await _get_week_schedule(group, session, monday)


async def _get_week_schedule(group: Union[str, Group],
                             session: aiohttp.ClientSession,
                             monday: Optional[datetime.date] = utils.get_week_monday()):
    return await get_schedule(group, monday, monday + datetime.timedelta(days=6), session)


async def get_real_group(group: str, session: aiohttp.ClientSession = None) -> Optional[str]:
    if session:
        return await _get_real_group(group, session)
    async with aiohttp.ClientSession() as session:
        return await _get_real_group(group, session)


async def _get_real_group(group: str, session: aiohttp.ClientSession) -> Optional[str]:
    params = dict(n=701, lev=142, faculty=0, query=group)
    async with session.get(URL, params=params) as groups_response:
        try:
            groups_json = await groups_response.json(content_type='text/html')
            for group_json in groups_json['suggestions']:
                if group.upper() == group_json.upper():
                    return group_json
            return None
        except JSONDecodeError:
            return None
