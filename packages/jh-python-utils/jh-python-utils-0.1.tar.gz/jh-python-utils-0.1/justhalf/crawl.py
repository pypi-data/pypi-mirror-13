# -*- coding: utf-8 -*-
"""
A collection of tools for crawling

Author: Aldrian Obaja <aldrianobaja.m@gmail.com>
Created: 16 Sep 2015
"""
import time
import requests
from justhalf.log import setup_logger

DELAY_BETWEEN_REQUESTS = 1.0
TIMEOUT = 35
last_request = time.time()


class Page(object):
    """A class to store HTTP response with caching capability"""
    def __init__(self, text, status_code=0, reason=None, from_cache=False, cached=False):
        self.text = text
        self.from_cache = from_cache
        self.cached = cached
        self.status_code = status_code
        self.reason = reason


class Crawler(object):
    _logger = setup_logger(__name__)

    def __init__(self, delay=1.0, timeout=60, retries=3, recovery_time=5):
        self.delay = delay
        self.timeout = timeout
        self.last_request = 0
        self.retries = retries
        self.recovery_time = recovery_time

    def get_page(self, url, session=requests, cache_coll=None):
        # Check cache
        if cache_coll is not None:
            cache = cache_coll.find_one({'url': url})
            if cache:
                Crawler._logger.info('Found {} in cache', url)
                return Page(cache['html'], from_cache=True)

        # Delay between requests
        sleep_time = max(0, self.delay - (time.time() - self.last_request))
        if sleep_time > 0:
            time.sleep(sleep_time)

        # Attempt to fetch page
        cached = False
        for retry in range(self.retries):
            try:
                html = session.get(url, timeout=self.timeout*(retry+1))
                self.last_request = time.time()
                is_ok = html.ok
                status = '{}: {}'.format(html.status_code, html.reason)
                if not is_ok:
                    if html.status_code == 504:
                        raise requests.exceptions.Timeout(status)
                    else:
                        raise requests.exceptions.HTTPError(status, response=html)
                try:
                    cache_coll.insert({'url': url, 'html': html.text})
                    cached = True
                except:
                    pass
                break
            except requests.exceptions.Timeout as e:
                if retry == self.retries-1:
                    raise e
                time.sleep(self.recovery_time)
        return Page(html.text,
                    status_code=html.status_code,
                    reason=html.reason,
                    from_cache=False,
                    cached=cached)


def _main():
    crawler = Crawler()
    page = crawler.get_page('http://google.com')
    print(page.text)

if __name__ == '__main__':
    _main()
