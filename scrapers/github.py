# -*- coding: utf-8 -*-
import logging
from grab.spider import Spider, Task
from .core.common import CommonMixin

logger = logging.getLogger('scrapers.github')


class GithubFavoritesScraper(Spider, CommonMixin):
    name = 'github_favorites'

    initial_urls = ['https://github.com/trending']

    def task_initial(self, grab, task):
        repos = grab.doc(
            '//ol[@class="repo-list"]//h3[@class="repo-list-name"]/a'
        ).attr_list('href')
        repos = map(
            grab.make_url_absolute,
            repos
        )
        for url in repos:
            yield Task('repo', url=url)

    def task_repo(self, grab, task):
        logger.info("Got page: {}".format(grab.response.url))

        commits = grab.doc(
            '//li[@class="commits"]//span[contains(@class, "num")]'
        ).text(default=u'')
        watchers = grab.doc(
            '//a[@class="social-count" and contains(@href, "/watchers")]'
        ).text(default=u'')
        forks = grab.doc(
            '//a[@class="social-count" and contains(@href, "/network")]'
        ).text(default=u'')
        stars = grab.doc(
            '//a[contains(@href, "/stargazers")]'
        ).text(default=u'')
        repo_name = grab.doc(
            '//h1[@class="entry-title public"]/strong/a'
        ).text(default=u'')

        author = grab.doc(
            '//span[@class="author"]//a[@rel="author"]'
        ).attr('href', default=u'')

        data = {
            'commits': int(commits.strip().replace(',', '')),
            'watchers': int(watchers.strip().replace(',', '')),
            'forks': int(forks.strip().replace(',', '')),
            'stars': int(stars.strip().replace(',', '')),
            'author': grab.make_url_absolute(author),
            'repo_name': repo_name.strip(),
            'source_url': grab.response.url,
        }

        self.save_item(self.name, ['source_url', 'author'], data)
