# -*- coding: utf-8 -*-
import logging
import argparse

from colorama import Fore, Style
from colorama import init as colorama_init
from weblib.logs import default_logging

from settings import (
    TASKS, ACTIVE_TASKS, BROKEN_TASKS, LOG_LEVEL)
from settings import db_connection
from utils.run_interface import ScrapersRunInterface

logger = logging.getLogger('cli')


def command_line_interface(parser):
    tasks_list = TASKS.keys()
    tasks_colored = []
    for task in tasks_list:
        if task in ACTIVE_TASKS:
            tasks_colored.append(
                Fore.GREEN + '*' + task + Style.RESET_ALL)
        elif task in BROKEN_TASKS:
            tasks_colored.append(
                Fore.RED + '!' + task + Style.RESET_ALL)
        else:
            tasks_colored.append(
                Fore.YELLOW + task + Style.RESET_ALL)

    task_help = "task to run (active marked with '*'):\n{}".format(
        ", ".join(tasks_colored))

    parser.add_argument('-T', '--task', type=str, help=task_help)
    parser.add_argument('-c', '--celery',
                        action="store_true", default=False,
                        help='run as celery task')

    args = parser.parse_args()
    return args


if __name__ == '__main__':  # noqa
    colorama_init()
    default_logging(grab_log='var/grab.log', level=LOG_LEVEL, mode='w',
                    propagate_network_logger=False,
                    network_log='var/grab.network.log')

    parser = argparse.ArgumentParser(description='command line interface')
    args = command_line_interface(parser)

    if args.task:
        if args.task == 'all':
            for task in ACTIVE_TASKS:
                scraper = ScrapersRunInterface.crawl(task)
                logger.info(scraper.render_stats())
        if args.task not in TASKS.keys():
            logger.critical(
                u"Can't find crawler in list: {}".format(
                    TASKS.keys()))
        if args.celery:
            # scraper_results = run_task.delay(args.task)
            # logger.info(scraper_results)
            pass
        else:
            scraper = ScrapersRunInterface.crawl(args.task)
            logger.info(scraper.render_stats())
    else:
        parser.print_help()
