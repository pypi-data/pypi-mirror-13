__author__ = 'Mwaaas'
__email__ = 'francismwangi152@gmail.com'
__phone_number__ = '+254702729654'

import logging
import os


class NotFound(object):
    def get(self, k, d=None):
        if d == self:
            return d
        return None


not_found = NotFound()


class CustomFilter(logging.Filter):

    def __init__(self):
        settings = os.environ.setdefault("DJANGO_SETTINGS_MODULE", "")
        self.environment = settings.split('.')[-1]
        super(CustomFilter, self).__init__()

    def filter(self, record):
        record.environment = self.environment
        return True
