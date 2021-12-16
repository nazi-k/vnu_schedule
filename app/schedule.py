"""Робота з розкладом - його додавання, видалення, нагадування, модерація"""
import datetime

from app import utils, exceptions, db

from app.models import WeekDay, Lesson, Schedule, Group, Subscriber, Subject
import app.vnu as vnu

from typing import Optional, Union, Iterable, List, Dict, Any


def add_schedule(schedule: Schedule) -> None:
    """Добавляє в БД: Lesson, Teacher, Group, WeekDay, Subject
       (дані з сторінки сайту)"""
    for weekday in schedule.weekdays:
        for lesson in weekday.lessons:
            get_or_create_subject(lesson.subject)
    _delete_lessons(schedule)
    add_lessons(schedule)
    add_group(schedule.group)
    add_teachers(schedule.get_teachers_name())


def _delete_lessons(schedule: Schedule) -> None:
    """Не комітить!!!!

    З розрахунком, що викликається перед добавлянням lessons, де відбувається коміт"""
    dates = schedule.get_dates()
    if dates:
        db.get_cursor().execute("DELETE FROM lesson where weekday_date "
                                f"BETWEEN  '{min(dates)}' AND '{max(dates)}' AND subject_id IN "
                                "(SELECT subject_id FROM 'lesson' JOIN 'subject' "
                                "where lesson.subject_id = subject.id"
                                f" and subject.group_name = '{schedule.group.name}')")


def add_lessons(schedule: Schedule) -> None:
    db.insert("lesson", schedule.get_weekdays_lessons_dict(), or_replace=True)


def get_or_create_subject(subject: Subject) -> Subject:
    """Повертає предмет з БД з полем id, якщо такого немає - створює і повертає

    Добавляє id в Subject переданий аргументом"""
    subject_id = _get_subject_id(subject)
    if not subject_id:
        db.insert("subject", [subject.to_dict()])
        subject_id = _get_subject_id(subject)
    subject.id = subject_id
    return subject


def _get_subject_id(subject: Subject) -> Optional[int]:
    subject_id = db.fetchone("subject", ["id"], subject.to_dict())
    return subject_id['id'] if subject_id else None


def add_group(group: Group):
    """Добавляє групу, якщо такої немає """
    db.insert("group_", [group.to_dict()], or_ignore=True)


def add_teachers(names: Iterable[str]):
    """Добавляє вчителя, якщо такого немає"""
    db.insert("teacher", [dict(name=name) for name in names], or_ignore=True)


def add_subscriber(subscriber: Subscriber) -> None:
    """Добавляє підписника і його налаштування"""
    db.insert('subscriber', [subscriber.to_dict()], or_replace=True)


def update_subscriber_group(telegram_id: int, group_name: str) -> None:
    """Змінює групу підписника"""
    db.update('subscriber', dict(group_name=group_name, is_moderator=False), dict(telegram_id=telegram_id))


def is_subscriber(telegram_id: Union[int, str]) -> bool:
    return bool(db.fetchone('subscriber', ['count(*)'], dict(telegram_id=telegram_id))['count(*)'])


def add_moderator(telegram_id: int) -> None:
    """Добавляє модератора групи"""
    db.update('subscriber', dict(is_moderator=True), dict(telegram_id=telegram_id))


async def get_weekday(subscriber: Subscriber, date: datetime.date = utils.today().date()) -> WeekDay:
    weekday = get_db_weekday(subscriber, date)
    if weekday.lessons:
        return weekday
    add_schedule(await vnu.get_week_schedule(subscriber.group_name, utils.get_week_monday(date)))
    return get_db_weekday(subscriber, date)


def get_db_weekday(subscriber: Subscriber, date: datetime.date = utils.today().date()) -> WeekDay:
    where_date_str = f"weekday_date = '{date}'"
    lessons_and_subjects = _get_db_lessons_and_subjects(subscriber, where_date_str)
    return WeekDay(date, [Lesson.db_init(lesson_and_subject) for lesson_and_subject in lessons_and_subjects])


async def get_week(subscriber: Subscriber, monday_date: datetime.date = utils.get_week_monday()) -> List[WeekDay]:
    week = get_db_week(subscriber, monday_date)
    if week:
        return week
    add_schedule(await vnu.get_week_schedule(subscriber.group_name, monday_date))
    return get_db_week(subscriber, monday_date)


def get_db_week(subscriber: Subscriber, monday_date: datetime.date = utils.get_week_monday()) -> List[WeekDay]:
    where_date_str = f"weekday_date BETWEEN '{monday_date}' AND '{monday_date + datetime.timedelta(days=6)}'"
    lessons_and_subjects = _get_db_lessons_and_subjects(subscriber, where_date_str)
    weekdays = []
    for lesson_and_subject in lessons_and_subjects:
        lesson = Lesson.db_init(lesson_and_subject)
        if not weekdays:
            weekdays.append(WeekDay(lesson.weekday_date, [lesson]))
        elif weekdays[-1].date == lesson.weekday_date:
            weekdays[-1].add_lesson(lesson)
        else:
            weekdays.append(WeekDay(lesson.weekday_date, [lesson]))
    return weekdays


def _get_db_lessons_and_subjects(subscriber: Subscriber, where_date_str: str) -> List[Dict[str, Any]]:
    """Повертає 'склеєні' таблиці (lesson JOIN subject JOIN online_lesson_url)

    number, start_time, end_time, weekday_date, form, audience, subgroup | id, name, group_name, teacher_name | url """
    where = f"WHERE {where_date_str} AND subject.group_name = '{subscriber.group_name}'" \
            f" AND subject.id = lesson.subject_id"
    if subscriber.subgroup:
        where += f" AND (subgroup IS NULL or subgroup = {subscriber.subgroup})"
    return db.fetchall("lesson JOIN  subject LEFT OUTER JOIN online_lesson_url"
                       " ON online_lesson_url.subject_id = subject.id",
                       ['number', 'start_time', 'end_time', 'weekday_date', 'form', 'audience', 'subgroup',  # lesson
                        'id', 'name', 'group_name', 'teacher_name',  # subject
                        'url'],  # online_lesson_url
                       where)


def get_subscriber(telegram_id: int) -> Subscriber:
    """Щоб знати, яку інформацію показувати в ТГ"""
    subscriber = db.fetchone('subscriber', ['telegram_id', 'group_name', 'reminder', 'subgroup',
                                            'show_online_link', 'notification_from_moderator', 'is_moderator'],
                             dict(telegram_id=telegram_id))
    if not subscriber:
        raise exceptions.NonTelegramID('Користувача не знайдено в підписниках')
    return Subscriber.db_init(subscriber)


def set_subscriber_settings(telegram_id: int, settings: Dict) -> None:
    """Змінює налаштування підписника"""
    db.update('subscriber', settings, dict(telegram_id=telegram_id))


def get_online_lesson_url_and_name(subject_id: int) -> Optional[Dict[str, str]]:
    """Повернути посилання або нічого, отже воно ще не встановлено"""
    where = f'WHERE subject.id = {subject_id}'
    online_lesson_url_and_name = db.fetchone('subject LEFT OUTER JOIN online_lesson_url on'
                                             ' online_lesson_url.subject_id = subject.id', ['url', 'name'], where)
    return online_lesson_url_and_name if online_lesson_url_and_name else None


def is_his_subject(telegram_id: int, subject_id: int) -> bool:
    where = f'where subscriber.group_name = subject.group_name and id = {subject_id} and telegram_id = {telegram_id}'
    return bool(db.fetchone('subscriber join subject', ['count(*)'], where)['count(*)'])


def get_his_group_moderator(telegram_id: int) -> Optional[int]:
    where = "where is_moderator is True and" \
            f" group_name = (SELECT group_name FROM subscriber where telegram_id = {telegram_id})"
    moderator_id = db.fetchone('subscriber', ['telegram_id'], where)
    return moderator_id['telegram_id'] if moderator_id else None


def is_moderator(telegram_id: int) -> bool:
    return bool(db.fetchone('subscriber', ['count(*)'], dict(telegram_id=telegram_id, is_moderator=1))['count(*)'])


def add_online_lesson_url(subject_id: int, url: str) -> None:
    """Добавляє посилання на онлайн заняття"""
    db.insert('online_lesson_url', [dict(subject_id=subject_id, url=url)], or_replace=True)


def get_subject_name(subject_id: int) -> str:
    return db.fetchone('subject', ['name'], dict(id=subject_id))['name']


def add_wait_subject_url(telegram_id: int, subject_id: int) -> None:
    db.insert('wait_subject_url', [dict(subscriber_telegram_id=telegram_id, subject_id=subject_id)], or_replace=True)


def get_wait_subject_url_subject_id(telegram_id: int) -> Optional[int]:
    subject_id_dict = db.fetchone('wait_subject_url', ['subject_id'], dict(subscriber_telegram_id=telegram_id))
    return subject_id_dict['subject_id'] if subject_id_dict else None


def get_subscribers_is_reminder() -> List[Subscriber]:
    subscribers = db.fetchall('subscriber', ['telegram_id', 'group_name', 'reminder', 'subgroup',
                                             'show_online_link', 'notification_from_moderator', 'is_moderator'],
                              dict(reminder='1'))
    return [Subscriber.db_init(subscriber) for subscriber in subscribers]


def get_telegram_id_is_notification(moderator_telegram_id) -> List[int]:
    where = f"where group_name = (SELECT group_name FROM 'subscriber' where telegram_id = {moderator_telegram_id})" \
            f" AND notification_from_moderator"
    return [telegram_id_dict["telegram_id"] for telegram_id_dict in db.fetchall("subscriber", ["telegram_id"], where)]


def get_all_group_name() -> List[str]:
    return [group["name"] for group in db.fetchall("group_", ["name"])]
