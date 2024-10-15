import datetime
from db import Configuration


def get_current_year():
    current_year = Configuration.query.filter_by(is_current_year=True).first()
    return current_year.year




