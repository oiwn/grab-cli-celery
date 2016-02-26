# -*- coding: utf-8 -*-
from datetime import datetime
from bson.objectid import ObjectId
from grab.spider import Spider

from settings import db_connection, TASKS, DEBUG
from utils.scrapers_factory import ScrapersFactory


class ScrapersRunInterface(object):
    tasks = TASKS
    db = db_connection()

    @classmethod
    def crawl(cls, task_name):
        scraper_module = cls.tasks[task_name]
        # save crawler status - started and store record _id into the database
        # used to log errors related to this scraper
        res = cls.save_stats(task_name, status='started')
        scraper_instance = ScrapersFactory.run_instance(
            scraper_module, use_cache=DEBUG, db_stats_record_id=res)
        cls.save_stats(task_name, scraper_instance=scraper_instance,
                       status='finished')
        return scraper_instance

    @classmethod
    def save_stats(cls, task_name, scraper_instance=None,
                   status='started'):
        """
        Save crawler statistic into the mongodb database.
        :param: status - could be in ['started', 'finished']
        """
        stats = {
            'task_name': task_name,
            'crawler': cls.tasks[task_name],
        }

        if status == 'started':
            stats['_created'] = datetime.utcnow()
            return cls.db['scrapersStats'].insert(stats)
        elif status == 'finished' and scraper_instance:
            stats['_finished'] = datetime.utcnow()
            stats_id = getattr(scraper_instance, 'db_stats_record_id')
            stats['_id'] = ObjectId(stats_id)

            if issubclass(scraper_instance.__class__, Spider):
                # ATTENTION: this one specific for Grab Spider
                # remove dot due to
                # bson.errors.InvalidDocument:
                # key 'response_handler.task_repo' must not contain '.'
                fixed_timers = {
                    k.replace('.', '_'):
                        v for k, v in scraper_instance.timer.timers.items()}
                fixed_counters = {}  # remove symbols python-eve can't render
                counters = scraper_instance.stat.counters
                for key, value in counters.items():
                    fixed_counters[
                        key.replace(':', '_').replace('-', '_')
                    ] = value

                # update grab scrapers stats collection
                return cls.db['scrapersStats'].update(
                    {
                        '_id': stats_id,
                    },
                    {
                        '$set': {
                            'timers': fixed_timers,
                            'counters': fixed_counters,
                            '_finished': datetime.utcnow(),
                        }
                    }
                )
            else:
                return cls.db['scrapersStats'].update(
                    {
                        '_id': stats_id,
                    },
                    {
                        '$set': {
                            '_finished': datetime.utcnow(),
                        }
                    }
                )
