# __author__ = 'ismailkaboubi'


import logging


class CustomAdapter(logging.LoggerAdapter):
    """
    This  adapter expects the passed in dict-like object to have a
    'ip' key, whose value in brackets is prepended to the log message.
    """
    def process(self, msg, kwargs):
        return '%s    %s    %s    %s' % (self.extra.get('ip', ''),
                                         self.extra.get('client', ''),
                                         self.extra.get('env', ''),
                                         msg), kwargs
