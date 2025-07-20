from datetime import datetime
import pytz

IST = pytz.timezone("Asia/Kolkata")


def get_current_ist_time():
    return datetime.now(IST)


def convert_to_ist(dt):
    return dt.astimezone(IST)
