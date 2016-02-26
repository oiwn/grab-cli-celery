# --*-- coding: utf-8 --*--
import os
import sys
import json
import logging
from datetime import timedelta

from pymongo import MongoClient

DEBUG = True
# set DEBUG value from os environment
if 'DEBUG' in os.environ:
    if os.environ['DEBUG'] == 'true':
        DEBUG = True
    elif os.environ['DEBUG'] == 'false':
        DEBUG = False

# backend
ENV = os.environ.get('ENV', 'development')
LOG_LEVEL = logging.DEBUG

if DEBUG is True:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

DB_NAME = 'data'
# http://docs.mongodb.org/manual/reference/connection-string/
DB_URI = 'mongodb://localhost:27017/{}'.format(DB_NAME)
if 'MONGO_URI' in os.environ:
    DB_URI = os.environ['MONGO_URI']

TASKS = {
    'github': 'scrapers.github.GithubFavoritesScraper',
}

SCRAPER_CONFIG = {
    'thread_number': int(os.environ.get('SCRAPER_THREADS', 5)),
    'network_try_limit': int(os.environ.get('NETWORK_TRY_LIMIT', 5)),
    'task_try_limit': int(os.environ.get('TASK_TRY_LIMIT', 5)),
    'max_task_generator_chunk': int(
        os.environ.get('MAX_TASK_GENERATOR_CHUNK', 10)),
    'priority_mode': os.environ.get('PRIORITY_MODE', 'const'),
}

# scraping
SCRAPING_USE_CACHE = True
SCRAPING_TASKS_CONFIG = os.environ.get(
    'SCRAPING_TASKS_CONFIG', 'scrapingtasks.json')
SCRAPING_TASKS = json.loads(open(SCRAPING_TASKS_CONFIG, 'r').read())
ACTIVE_TASKS = SCRAPING_TASKS['active']
BROKEN_TASKS = SCRAPING_TASKS['broken']

# Celery configuration
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
SCRAPING_INTERVAL = int(os.environ.get('SCRAPING_INTERVAL', 48))

CELERYBEAT_SCHEDULE = {
    'run-crawlers': {
        'task': 'tasks.run_chain',
        'schedule': timedelta(hours=SCRAPING_INTERVAL),
        'args': ACTIVE_TASKS,
    }
}

CELERY_CONFIG = {
    'CELERY_IMPORTS': ('tasks', ),
    'CELERY_TASK_SERIALIZER': 'json',
    'CELERY_ACCEPT_CONTENT': ['json'],
    'CELERY_TIMEZONE': 'UTC',
    'CELERYBEAT_SCHEDULE': CELERYBEAT_SCHEDULE,
}

def db_connection(db_name=None):
    client = MongoClient(DB_URI.format(''))
    if db_name is None:
        return client[DB_NAME]
    else:
        return client[db_name]
