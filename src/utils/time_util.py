from datetime import datetime
import pytz

IST = pytz.timezone("Asia/Kolkata")


def get_current_ist_time():
    return datetime.now(IST)


def current_date_str():
    return get_current_ist_time().strftime('%d-%m-%Y')


def convert_to_ist(dt):
    return dt.astimezone(IST)
