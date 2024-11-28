import datetime
from db import Year


def get_current_year():
    current_year = Year.query.filter_by(is_current_year=True).first()
    return current_year.year




