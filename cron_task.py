from celery import Celery
from celery.task import periodic_task
from vibesify_beat_config import *
from datetime import timedelta
from vibesify_job import *
import time
import datetime

app = Celery('cron_task', broker='amqp://guest@localhost//')

@periodic_task(run_every=timedelta(hours = VIBESIFY_BEAT_FREQUENCY))
def vibesify_task():
    now = datetime.datetime.now()
    timestamp = time.mktime(now.timetuple()) * 1e3
    vibesify(timestamp)