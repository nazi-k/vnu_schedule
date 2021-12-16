create table teacher(
    name varchar(255) primary key,
    id integer
);

create table group_(
    name nchar(20) primary key,
    id integer
);

create table subject(
    id integer primary key,
    name varchar(255),
    group_name nchar(20),
    teacher_name varchar(255),
    FOREIGN KEY(group_name) REFERENCES group_(name),
    FOREIGN KEY(teacher_name) REFERENCES teacher(name)
);

create table lesson(
    number integer,
    start_time nchar(20),
    end_time nchar(20),
    weekday_date date,
    subject_id integer,
    form nchar(20),
    audience nchar(20),
    subgroup integer,
    FOREIGN KEY(subject_id) REFERENCES subject(id)
);

create table online_lesson_url(
    subject_id integer primary key,
    url varchar(255),
    FOREIGN KEY(subject_id) REFERENCES subject(id)
);

create table subscriber(
    telegram_id integer primary key,
    group_name nchar(20),
    reminder boolean,
    subgroup integer,
    show_online_link boolean,
    notification_from_moderator boolean,
    is_moderator boolean,
    FOREIGN KEY(group_name) REFERENCES group_(name)
);

create table wait_subject_url(
    subscriber_telegram_id integer primary key,
    subject_id integer,
    FOREIGN KEY(subscriber_telegram_id) REFERENCES subscriber(telegram_id),
    FOREIGN KEY(subject_id) REFERENCES subject(id)
)