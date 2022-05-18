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
from .utils import RateWareTariffLoader


def main(mytimer: func.TimerRequest) -> None:
    start_time = time.time()
    logging.info("--- RateBase RateWare Load Starting")

    loader = RateWareTariffLoader()
    loader.load_available_tariffs(True)
    loader.load_db_base_rates(True)
    loader.update_db_rate_bases(True)
    loader.save_rate_bases(True)

    logging.info("--- RateBase RateWare Load Completed in %s seconds ---" % (time.time() - start_time))
