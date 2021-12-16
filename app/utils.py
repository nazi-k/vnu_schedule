import datetime


class UA(datetime.tzinfo):
    def utcoffset(self, dt):
        return datetime.timedelta(hours=2)

    def dst(self, dt):
        return datetime.timedelta(0)


def today(tz: datetime.tzinfo = UA()) -> datetime.datetime:
    return datetime.datetime.now(tz)


def get_week_monday(date: datetime.date = today().date()) -> datetime.date:
    return date - datetime.timedelta(days=date.weekday())


def str_to_time(time: str, seconds: bool = False) -> datetime.time:
    return datetime.datetime.strptime(time, f'%H:%M{":%S" if seconds else ""}').time()


def str_to_date(date: str) -> datetime.date:
    return datetime.datetime.strptime(date, "%Y-%m-%d").date()


def get_d_m_y(date: datetime.date) -> str:
    return date.strftime('%d.%m.%Y')


def get_weekday_name(weekday_date: datetime.date) -> str:
    weekdays_name = ["Понеділок", "Вівторок", "Середа", "Четвер", "П'ятниця", "Субота", "Неділя"]
    return weekdays_name[weekday_date.weekday()]
