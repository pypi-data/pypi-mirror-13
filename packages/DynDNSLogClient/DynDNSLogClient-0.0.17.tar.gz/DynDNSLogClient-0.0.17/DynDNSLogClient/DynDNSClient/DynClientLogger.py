import time
import os
import logging
import errno

"""
Class that automatically handles log rotation
"""
class Logger(object):
    """
    Initialize the class
    """
    def __init__(self):
        ts = int(time.time())
        self.ts = ts - (ts % 86400)
        self.logger = None
        self.handler = None
        self.initLog()

    """
    Initialize logging
    """
    def initLog(self):
        # Logging stuff
        tstruct = time.gmtime()
        logname = 'dyndns_' + str(tstruct.tm_year).zfill(4) + str(tstruct.tm_mon).zfill(2) + str(tstruct.tm_mday).zfill(
            2) + '.log'

        # Log directory is colocated
        logPath = os.path.dirname(os.path.realpath(__file__)) + '/..'
        logPath += '/log/' + logname
        self.logger = logging.getLogger("dyn_dns_log_client")
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

        # Make sure the path exists
        if not os.path.exists(logPath):
            index = logPath.rfind('/')
            if index == -1:
                index = 0
            dirs = logPath[:index] + '/'
            self.mkdirp(dirs)

        self.handler = logging.FileHandler(logPath)
        self.handler.setFormatter(formatter)
        self.logger.addHandler(self.handler)

        return self.logger, self.handler

    """
    Check rollover
    """
    def checkRollover(self):
        now_ts = int(time.time())
        new_ts = now_ts - (now_ts % 86400)

        if new_ts != self.ts:
            self.ts = new_ts
            self.logger.removeHandler(self.handler)
            self.initLog()

    """
    Replicates 'mkdir -p'
    """
    def mkdirp(self, path):
        try:
            os.makedirs(path)
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise


