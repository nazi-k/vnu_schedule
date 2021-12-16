from bs4 import BeautifulSoup
import re
import datetime
import bs4

import app.exceptions as exceptions
from app.models import WeekDay, Lesson, Form, Group, Schedule, Subject

from typing import List, Dict, Optional


def get_schedule(html: str) -> Schedule:
    bs = BeautifulSoup(html, 'html.parser')
    try:
        group_tag = bs.find('a')
        group_id = re.findall(r'\./timetable\.cgi\?n=700&amp;group=(\d+)', str(group_tag))[0]
        group = Group(id=group_id, name=group_tag.text)
    except IndexError:
        raise exceptions.NonGroup('Групу не знайдено')

    weekdays = []

    lessons_info = bs.find_all('tr')
    for lesson_info in lessons_info:
        if _is_lesson(lesson_info.text):
            date = _get_date(lesson_info.parent.parent.h4.text)

            lesson_number_soup, lesson_time_soup, lessons_description_soup = lesson_info.contents

            lesson_number = int(lesson_number_soup.text)
            start_time, end_time = _get_time_limits(lesson_time_soup.text)
            for lesson_tag in _get_lessons_tag(lessons_description_soup):
                try:
                    lesson_description = _get_lesson_description(lesson_tag)
                    lesson = Lesson(number=lesson_number,
                                    start_time=start_time,
                                    end_time=end_time,
                                    weekday_date=date,
                                    subject=Subject(name=lesson_description['subject'],
                                                    group_name=group.name,
                                                    teacher_name=lesson_description['teacher']),
                                    form=lesson_description['lesson_form'],
                                    audience=lesson_description['audience'],
                                    subgroup=lesson_description['subgroup'])
                except exceptions.ScheduleError:
                    lesson = Lesson(number=lesson_number,
                                    start_time=start_time,
                                    end_time=end_time,
                                    weekday_date=date,
                                    subject=Subject(name=lessons_description_soup.text, group_name=group.name))
                finally:
                    if not weekdays:
                        weekdays.append(WeekDay(date, [lesson]))
                    elif weekdays[-1].date == date:
                        weekdays[-1].add_lesson(lesson)
                    else:
                        weekdays.append(WeekDay(date, [lesson]))
    return Schedule(group=group, weekdays=weekdays)


def _get_audience(lesson_description_text: str) -> Optional[str]:
    try:
        return re.findall(r'ауд\. (\w-\d+)', lesson_description_text)[0]
    except IndexError:
        return None


def _get_teacher(lesson_description_text: str) -> Optional[str]:
    try:
        return re.findall(r'\w+\s\w\.\w\.|\w+\s\(\w\)\s\w\.\w\.', lesson_description_text)[0]
    except IndexError:
        return None


def _get_discipline(lesson_description_text: str) -> str:
    return Form.get_compile().split(lesson_description_text)[0].strip()


def _get_format(lesson_description: str) -> Form:
    form = Form.get_compile().findall(lesson_description)
    if not form:
        raise exceptions.NonForm('Вдсутня форма проведення')
    return Form.get_form(form[0])


def _is_lesson(lesson_info: str) -> bool:
    return bool(re.findall(r'[^\d: ]', lesson_info))


def _get_date(date: str) -> datetime.date:
    return datetime.datetime.strptime(re.findall(r'\d\d\.\d\d\.\d{4}', date)[0], "%d.%m.%Y").date()


def _get_time_limits(time_limits: str) -> map:
    return map(lambda time: datetime.datetime.strptime(time, "%H:%M").time(), re.findall(r'\d\d:\d\d', time_limits))


def _get_lesson_description(lesson_description: bs4.element.Tag) -> Dict:
    if '(підгр. 1)' in lesson_description.text:
        subgroup = 1
    elif '(підгр. 2)' in lesson_description.text:
        subgroup = 2
    else:
        subgroup = None
    subject = _get_discipline(lesson_description.text)
    lesson_form = _get_format(lesson_description.text)
    teacher = _get_teacher(lesson_description.text)
    audience = _get_audience(lesson_description.text)
    return dict(subgroup=subgroup,
                subject=subject,
                lesson_form=lesson_form,
                teacher=teacher,
                audience=audience)


def _get_lessons_tag(lessons_description_soup: bs4.element.Tag) -> List[bs4.element.Tag]:
    lessons_description = []
    for lesson_description in str(lessons_description_soup).split('<div class="link"> </div>'):
        lesson_description_soup = BeautifulSoup(lesson_description, 'html.parser')
        if lesson_description_soup.text.replace(' ', ''):
            lessons_description.append(lesson_description_soup)
    return lessons_description
