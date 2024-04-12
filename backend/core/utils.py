import datetime


def append_data(date, *args, **kwargs):
    return date + datetime.timedelta(*args, **kwargs)


def plural_days(n):
    days = ["день", "дня", "дней"]
    if n:
        if n % 10 == 1 and n % 100 != 11:
            return " ".join([str(n), days[0]])
        elif 2 <= n % 10 <= 4 and (n % 100 < 10 or n % 100 >= 20):
            return " ".join([str(n), days[1]])
        else:
            return " ".join([str(n), days[2]])
    else:
        return None
