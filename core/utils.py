from datetime import datetime
import pytz
from django.conf import settings

def now() -> datetime:
    return datetime.now(tz=pytz.timezone(settings.TIME_ZONE))