from app import db
from app.utils import get_week_monday

import datetime


def clean_db():
    delete_wait_subject_url()
    delete_schedule_older_than(get_week_monday() - datetime.timedelta(days=14))


def delete_wait_subject_url():
    db.delete('wait_subject_url', '')


def delete_schedule_older_than(date: datetime.date):
    where = f"WHERE weekday_date < {date}"
    db.delete('lesson', where)
