# -*- coding: utf-8 -*-
import logging
import pycurl

from grab.spider import Spider

from settings import (
    DEBUG, SCRAPING_USE_CACHE,
    SCRAPER_CONFIG, DB_URI, DB_NAME
)
from .moduleimport import module_import
from scrapers.core.common import CommonMixin

logger = logging.getLogger('scrapers.factory')


class ScrapersFactory(object):
    """ Configure grab spider instance
    """
    @classmethod
    def get_instance(cls, spider_class, use_proxy=False,
                     use_cache=False, **kwargs):
        """ Configure bot instance.
        """

        if isinstance(spider_class, basestring):
            print spider_class
            spider_cls = module_import(spider_class)
        else:
            spider_cls = spider_class

        # create crawler instance depends on type (grab, selenium etc.)
        if issubclass(spider_cls, Spider) or issubclass(spider_cls, CommonMixin):
            # if crawler instance is grab Spider object
            logger.info("Setup grab crawler instance...")
            bot = spider_cls(**SCRAPER_CONFIG)

            if use_proxy:
                # need proxy list
                bot.load_proxylist('var/proxylist.txt', 'text_file', 'http',
                                   auto_change=True)
            if use_cache:
                host = DB_URI.format('')  # leave database param empty

                bot.setup_cache(
                    backend='mongo',
                    database=DB_NAME,
                    use_compression=True, host=host)

            bot.create_grab_instance(timeout=20, connect_timeout=20)
        else:
            logger.fatal(u"This crawler type is not implemented")
            raise NotImplementedError

        # pass as attributes into the scraper
        for key, value in kwargs.items():
            setattr(bot, key, value)

        return bot

    @classmethod
    def run_instance(cls, spider_class, use_proxy=False,
                     use_cache=SCRAPING_USE_CACHE, **kwargs):
        """ Configure and run bot instance
        """
        logger.info(u"Debug: {}".format(DEBUG))
        logger.info(u"pycurl - {}".format(pycurl.version))
        logger.info(u"proxies: {} cache: {}".format(use_proxy, use_cache))
        scraper_instance = cls.get_instance(
            spider_class, use_proxy=use_proxy, use_cache=use_cache, **kwargs)
        scraper_instance.run()
        return scraper_instance
