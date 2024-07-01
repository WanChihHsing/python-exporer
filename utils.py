import datetime


def get_last_week_range():
    today = datetime.date.today()
    start_of_this_week = today - datetime.timedelta(days=today.weekday())
    start_of_last_week = start_of_this_week - datetime.timedelta(days=7)
    end_of_last_week = start_of_last_week + datetime.timedelta(days=6)
    return start_of_last_week, end_of_last_week
