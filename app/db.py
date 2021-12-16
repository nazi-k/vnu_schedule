import os

import sqlite3
import datetime
from typing import Dict, List, Any, Union

conn = sqlite3.connect(os.path.join("db", "schedule.db"))
cursor = conn.cursor()


def _get_where(where: Union[Dict, str]) -> str:
    """Якщо dict,то поєднує всі значення з використанням AND"""
    if isinstance(where, str):
        return where
    else:
        return ('WHERE ' + ' and '.join(list(map(' = '.join, [
            (key, f"'{str(value)}'" if type(value) in (str, datetime.date) else str(value))
            for key, value in where.items()
        ])))).replace('= None', 'is NULL')


def insert(table: str, column_values: List[Dict], or_ignore: bool = False, or_replace: bool = False):
    """Всі key в column_values мають бути одинакові"""
    if not column_values:
        return
    columns = ', '.join(column_values[0].keys())
    values = [tuple(value.values()) for value in column_values]
    placeholders = ", ".join("?" * len(column_values[0].keys()))
    cursor.executemany(
        f"INSERT {'OR IGNORE' if or_ignore else 'OR REPLACE' if or_replace else ''} INTO {table} "
        f"({columns}) "
        f"VALUES ({placeholders})",
        values)
    conn.commit()


def fetchall(table: str, columns: List[str], where: Union[Dict, str] = '') -> List[Dict[str, Any]]:
    where = _get_where(where)
    columns_joined = ", ".join(columns)
    cursor.execute(f"SELECT {columns_joined} FROM {table} {where}")
    rows = cursor.fetchall()
    result = []
    for row in rows:
        dict_row = {}
        for index, column in enumerate(columns):
            dict_row[column] = row[index]
        result.append(dict_row)
    return result


def fetchone(table: str, columns: List[str], where: Union[Dict, str] = '') -> Dict[str, Any]:
    where = _get_where(where)
    columns_joined = ", ".join(columns)
    cursor.execute(f"SELECT {columns_joined} FROM {table} {where}")
    row = cursor.fetchone()
    dict_row = {}
    for index, column in enumerate(columns):
        try:
            dict_row[column] = row[index]
        except TypeError:
            return dict_row
    return dict_row


def delete(table: str, where: Union[Dict, str]) -> None:
    cursor.execute(f"delete from {table} {_get_where(where)}")
    conn.commit()


def update(table: str, column_values: Dict, where: Union[Dict, str]) -> None:
    set_str = ', '.join(tuple(map(' = '.join,
                              [(key, f"'{str(value)}'" if type(value) in (str, datetime.datetime) else str(value))
                               for key, value in column_values.items()])))
    where_str = _get_where(where)
    cursor.execute(
        f"Update {table} "
        f"SET {set_str} "
        f" {where_str}")
    conn.commit()


def get_cursor():
    return cursor


def _init_db():
    """Ініціалізує БД"""
    with open(os.path.join("db", "createdb.sql"), "r") as f:
        sql = f.read()
    cursor.executescript(sql)
    conn.commit()


def check_db_exists():
    """Перевіряє, чи ініціалізована БД, якщо ні — ініціалізує"""
    cursor.execute("SELECT name FROM sqlite_master "
                   "WHERE type='table' AND name='subject'")
    table_exists = cursor.fetchall()
    if table_exists:
        return
    _init_db()


check_db_exists()
