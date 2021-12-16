import datetime
import re
from typing import NamedTuple, List, Dict, Optional, Set

import app.utils as utils


class Form:
    """Форми проведення заннять
    Атрибути класу - вивід в повідомлення тг"""
    lecture = 'Лекція'
    practical = 'Практична'
    laboratory = 'Лабораторна'
    test = 'Залік'
    exam = 'Екзамен'

    @staticmethod
    def get_compile():
        """Для пошуку на сайті університету"""
        return re.compile(r'\(Лаб\)|\(Л\)|\(Пр\)|\(Зал\)|\(Екз\)')

    @classmethod
    def get_form(cls, pattern: str):
        """Повертає формат для виводу в тг"""
        if pattern == '(Лаб)':
            return cls.laboratory
        if pattern == '(Л)':
            return cls.lecture
        if pattern == '(Пр)':
            return cls.practical
        if pattern == '(Зал)':
            return cls.test
        if pattern == '(Екз)':
            return cls.exam


class Subject:

    def __init__(self,
                 name: str,
                 group_name: str,
                 teacher_name: Optional[str] = None,
                 id: Optional[int] = None,
                 url: Optional[str] = None):
        self.name = name
        self.group_name = group_name
        self.teacher_name = teacher_name
        self.id = id
        self.url = url

    def to_dict(self) -> Dict:
        subject_dict = dict(name=self.name,
                            group_name=self.group_name)
        if self.teacher_name:
            subject_dict.update(dict(teacher_name=self.teacher_name))
        if self.url:
            subject_dict.update(dict(url=self.url))
        return subject_dict

    def __eq__(self, cls) -> bool:
        return self.name == cls.name and self.group_name == cls.group_name and self.teacher_name == cls.teacher_name


class Lesson:
    """Урок з описом розділеним між полями"""

    def __init__(self,
                 number: int,
                 start_time: datetime.time,
                 end_time: datetime.time,
                 weekday_date: datetime.date,
                 subject: Subject,
                 form: Optional[Form] = None,
                 audience: Optional[str] = None,
                 subgroup: Optional[int] = None):
        self.number = number
        self.start_time = start_time
        self.end_time = end_time
        self.weekday_date = weekday_date
        self.subject = subject
        self.form = form
        self.audience = audience
        self.subgroup = subgroup

    def to_dict(self) -> Dict:
        return dict(number=self.number,
                    start_time=str(self.start_time)[:-3],
                    end_time=str(self.end_time)[:-3],
                    weekday_date=str(self.weekday_date),
                    subject_id=self.subject.id,
                    form=self.form,
                    audience=self.audience,
                    subgroup=self.subgroup)

    @staticmethod
    def db_init(lesson_and_subject: Dict):
        """Повертає Lesson створений з даних з БД"""
        return Lesson(number=lesson_and_subject['number'],
                      start_time=utils.str_to_time(lesson_and_subject['start_time']),
                      end_time=utils.str_to_time(lesson_and_subject['end_time']),
                      weekday_date=utils.str_to_date(lesson_and_subject['weekday_date']),
                      form=lesson_and_subject['form'],
                      audience=lesson_and_subject['audience'],
                      subgroup=lesson_and_subject['subgroup'],
                      subject=Subject(name=lesson_and_subject['name'],
                                      group_name=lesson_and_subject['group_name'],
                                      teacher_name=lesson_and_subject['teacher_name'],
                                      id=lesson_and_subject['id'],
                                      url=lesson_and_subject['url']))


class WeekDay:
    """Розклад навчального деня"""

    def __init__(self, date: datetime.date, lessons: List[Lesson]):
        self.date = date
        self.lessons = lessons

    def add_lesson(self, lesson: Lesson) -> None:
        self.lessons.append(lesson)

    def get_lessons_dict(self) -> List[Dict]:
        return [lesson.to_dict() for lesson in self.lessons]

    def get_subjects_dict(self) -> List[Dict]:
        subjects = []
        for lesson in self.lessons:
            if lesson.subject not in subjects:
                subjects.append(lesson.subject)
        return [subject.to_dict() for subject in subjects]

    def get_teachers_name(self) -> Set[str]:
        return {lesson.subject.teacher_name for lesson in self.lessons}


class Group:
    """Структура даних групи"""

    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name

    def __str__(self):
        return self.name

    def to_dict(self) -> dict:
        return dict(id=self.id, name=self.name)


class Schedule(NamedTuple):
    """Структура даних розкладу для певної групи"""
    group: Group
    weekdays: List[WeekDay]

    def get_weekdays_lessons_dict(self) -> List[Dict]:
        weekdays_lessons_dict = []
        for weekday in self.weekdays:
            weekdays_lessons_dict.extend(weekday.get_lessons_dict())
        return weekdays_lessons_dict

    def get_weekdays_subjects_dict(self) -> List[Dict]:
        weekdays_subjects_dict = []
        for weekday in self.weekdays:
            weekdays_subjects_dict.extend(weekday.get_subjects_dict())
        return weekdays_subjects_dict

    def get_teachers_name(self) -> Set[str]:
        teachers_name = set()
        for weekday in self.weekdays:
            teachers_name |= weekday.get_teachers_name()
        return teachers_name

    def get_dates(self):
        return [weekday.date for weekday in self.weekdays]


class Subscriber:
    def __init__(self, telegram_id: int,
                 group_name: str,
                 subgroup: int = 0,
                 reminder: bool = True,
                 show_online_link: bool = True,
                 notification_from_moderator: bool = True,
                 is_moderator: bool = False):
        self.telegram_id = telegram_id
        self.group_name = group_name
        self.subgroup = subgroup
        self.reminder = reminder
        self.show_online_link = show_online_link
        self.notification_from_moderator = notification_from_moderator
        self.is_moderator = is_moderator

    def to_dict(self) -> Dict:
        return dict(telegram_id=self.telegram_id,
                    group_name=self.group_name,
                    subgroup=self.subgroup,
                    reminder=self.reminder,
                    show_online_link=self.show_online_link,
                    notification_from_moderator=self.notification_from_moderator,
                    is_moderator=self.is_moderator)

    @classmethod
    def db_init(cls, db_subscriber: Dict):
        return Subscriber(telegram_id=db_subscriber['telegram_id'],
                          group_name=db_subscriber['group_name'],
                          subgroup=db_subscriber['subgroup'],
                          reminder=db_subscriber['reminder'],
                          show_online_link=db_subscriber['show_online_link'],
                          notification_from_moderator=db_subscriber['notification_from_moderator'],
                          is_moderator=db_subscriber['is_moderator'])
