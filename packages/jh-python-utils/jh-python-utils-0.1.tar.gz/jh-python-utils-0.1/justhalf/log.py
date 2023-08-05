# -*- coding: utf-8 -*-
"""
Log related functions and classes

Author: Aldrian Obaja <aldrianobaja.m@gmail.com>
Created: 16 Sep 2015
"""
from six import print_
import time
from datetime import datetime
import logging


def setup_logger(name):
    logger = logging.getLogger(name)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(fmt='[%(asctime)s]%(message)s', datefmt='%Y-%m-%d %H:%M:%S.%f')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


class Timing(object):
    """A context manager that prints the execution time of the block it manages"""

    def __init__(self, message, logger=None, one_line=True):
        self.message = message
        if logger is not None:
            self.default_logger = False
            self.one_line = False
            self.logger = logger
        else:
            self.default_logger = True
            self.one_line = one_line
            self.logger = None

    def _log(self, message, newline=True):
        if self.default_logger:
            print_(message, end='\n' if newline else '', flush=True)
        else:
            self.logger.info(message)

    def __enter__(self):
        self.start = time.time()
        self._log(self.message, not self.one_line)

    def __exit__(self, exc_type, exc_value, traceback):
        self._log('{}Done in {:.3f}s'.format('' if self.one_line else self.message, time.time()-self.start))


def tprint(message):
    """A quick method to print messages prepended with time information"""
    print_('[{}]{}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3], message))


def _main():
    tprint('Hello World!')
    root_logger = logging.getLogger()
    logging.basicConfig(level=logging.INFO)
    root_logger.info('Before sleeping')
    with Timing('Sleeping for 1 seconds...'):
        time.sleep(1)
    with Timing('Doing work...', root_logger):
        root_logger.info('This is the work')
    root_logger.info('After doing work')

if __name__ == '__main__':
    _main()
