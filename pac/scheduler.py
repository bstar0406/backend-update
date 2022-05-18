from apscheduler.schedulers.background import BackgroundScheduler

# logging.basicConfig(level=logging.DEBUG)
from pac.rrf.tasks import validate, status_watcher
from django.conf import settings


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(validate, 'interval', seconds=settings.AP_SCHEDULER_INTERVAL_VALIDATE)
    scheduler.add_job(status_watcher, 'interval', seconds=settings.AP_SCHEDULER_INTERVAL_STATUS_WATCHER)

    if settings.AP_SCHEDULER_ENABLE:
        scheduler.start()
