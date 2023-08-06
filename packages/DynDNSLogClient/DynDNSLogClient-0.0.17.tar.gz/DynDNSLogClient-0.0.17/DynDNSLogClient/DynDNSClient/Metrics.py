import time

"""
Metrics class for informational logging
"""
class Metrics(object):
    """
    Initialization
    """
    def __init__(self, logger):
        self.dLogger = logger
        self.MSG_CALLS = "API calls in last 5 minutes"
        self.MSG_CALLS_WITH_DATA = "API calls in last 5 minutes resulting in data"
        self.MSG_RECVD = "Messages received in last 5 minutes (can be multiple per API call)"
        self.KBYTES_RECV = "KBytes received in last 5 minutes (raw)"
        self.KBYTES_WRITTEN = "KBytes written in last 5 minutes"
        self.LATE_KB = "Late KBytes written in last 5 minutes"
        self.CURRENT_KB = "Current KBytes written in last 5 minutes"
        self.PREV_KB = "Previous KBytes written in last 5 minutes"
        self.metrics = {}
        self.lastWrite = time.time()
        self.metrics[self.KBYTES_RECV] = 0
        self.metrics[self.KBYTES_WRITTEN] = 0
        self.metrics[self.MSG_RECVD] = 0
        self.metrics[self.MSG_CALLS] = 0
        self.metrics[self.MSG_CALLS_WITH_DATA] = 0
        self.metrics[self.LATE_KB] = 0
        self.metrics[self.CURRENT_KB] = 0
        self.metrics[self.PREV_KB] = 0
        self.ORDER = [self.MSG_CALLS, self.MSG_CALLS_WITH_DATA, self.MSG_RECVD, self.KBYTES_RECV, self.KBYTES_WRITTEN, self.CURRENT_KB, self.PREV_KB, self.LATE_KB]

    """
    Add to a metric
    """
    def Add(self, key, value):
        if not key in self.metrics:
            self.metrics[key] = 0
        self.metrics[key] += value

    """
    Output to log
    """
    def Output(self):
        metrics_out = "Performance metrics:\n"
        for key in self.ORDER:
            metrics_out += ('  ' + key + ': ')
            metrics_out += (str(self.metrics[key]) + '\n')
            self.metrics[key] = 0
        self.dLogger.logger.info(metrics_out)
        self.lastWrite = time.time()
        return

