import datetime
import logging
import os
import json
import time
import azure.functions as func

# Load Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pac.settings.settings')  # nopep8
from django.core.wsgi import get_wsgi_application  # nopep8
application = get_wsgi_application()  # nopep8
# Change to django.setup() instead of wsgi

from pac.rrf.models import Request  # nopep8
from .utils import RequestDeadlineNotification


def main(mytimer: func.TimerRequest) -> None:
    start_time = time.time()
    logging.info("--- Overdue Notification Load Starting")

    loader = RequestDeadlineNotification()
    loader.load_overdue_requests(True)
    loader.send_overdue_request_notifications(True)

    logging.info("--- Overdue Notification Load Completed in %s seconds ---" % (time.time() - start_time))
