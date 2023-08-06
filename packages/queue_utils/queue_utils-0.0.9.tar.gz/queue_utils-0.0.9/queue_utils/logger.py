import logging


class Logable(object):

    def __init__(self, *args, **kwargs):
        self._logger = Logger(*args, **kwargs)

        self.error = self._logger.error
        self.debug = self._logger.debug
        self.info = self._logger.info


class Logger(object):

    def __init__(self, *args, **kwargs):
        ids = []
        for a in args:
            if a:
                ids.append(str(a))
        for k, v in kwargs.iteritems():
            ids.append("%s=%s" % (k, v))

        self.logger_name = '.'.join(i for i in ids)
        self._logger = logging.getLogger(self.logger_name)

    def debug(self, msg, *args, **kwargs):
        self.log(logging.DEBUG, msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self.log(logging.INFO, msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self.log(logging.ERROR, msg, *args, **kwargs)

    def log(self, lvl, msg, *args, **kwargs):
        """
        Perform logging for the worker.
        """
        self._logger.log(lvl, msg, *args, **kwargs)
