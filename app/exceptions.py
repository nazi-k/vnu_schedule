class ScheduleError(Exception):
    pass


class NonForm(ScheduleError):
    pass


class NonGroup(ScheduleError):
    pass


class SubscriberError(Exception):
    pass


class NonTelegramID(SubscriberError):
    pass
