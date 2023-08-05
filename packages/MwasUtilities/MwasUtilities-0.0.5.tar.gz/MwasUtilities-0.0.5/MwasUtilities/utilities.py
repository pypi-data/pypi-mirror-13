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


class LogDjangoSetting(logging.Filter):

    def __init__(self):
        settings = os.environ.setdefault("DJANGO_SETTINGS_MODULE", "")
        self.environment = settings.split('.')[-1]
        super(LogDjangoSetting, self).__init__()

    def filter(self, record):
        record.environment = self.environment
        return True


class LogOsEnvironment(logging.Filter):

    def __init__(self, env_variable):
        self.env_variable = os.environ.get(env_variable, None)
        super(LogOsEnvironment, self).__init__()

    def filter(self, record):
        record.os_variable = self.env_variable
        return True
