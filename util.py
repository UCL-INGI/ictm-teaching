import datetime


def get_current_year():
    current_date = datetime.date.today()
    current_year = current_date.year
    if current_date.month >= 9:  # Assuming academic year starts in September
        return current_year + 1
    else:
        return current_year
