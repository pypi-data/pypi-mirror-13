import logging


class Logable(object):

    def __init__(self, name, id):
        self._logger = Logger(name, id)

        self.error = self._logger.error
        self.debug = self._logger.debug
        self.info = self._logger.info


class Logger(object):

    def __init__(self, name, id):
        if id is not None:
            self.logger_name = '%s.%s' % (name, id)
        else:
            self.logger_name = name

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
