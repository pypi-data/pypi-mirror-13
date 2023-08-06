#!/usr/bin/python -OO

"""
    Copyright(c) Dyn, Inc.
    License ????

    Usage:

    *** Needs unit tests ***

    This Python program requires that the following be installed (we use pip):

        'sudo apt-get install' or 'sudo yum install' python-pip

            To run this script directly, install the following dependencies:
                sudo pip install iron-mq
                sudo pip install python-daemon
                sudo pip install simplejson
            But we should package this script and upload it to PyPi, then a user simply must:
                sudo pip install DynDNSLogClient

    A configuration file called 'DynDNSLogClient.json' must be co-located with this script.
    It must be supplied by Dyn with the proper values (endpoint, projectid, token, etc).

    If this script is started as the root user, the pid file will be placed in /var/run.
    Otherwise it will be placed in {script directory}/run

    This script is run as a deamon, i.e. "./DynDNSLogClient.py start"


    Interesting perf metrics:
        KBytes per second (updated 5 minutes for last 10 minutes)

"""

from iron_mq import *
import sys
from daemon import runner
import os
import glob
import errno
import time
import signal
import datetime
import base64
import snappy
from DynDNSClient.Configuration import Configuration
from DynDNSClient.Metrics import Metrics
from DynDNSClient.FileWriter import FileWriter
from DynDNSClient.DynClientLogger import Logger

# Globals
DEFAULT_CONFIG_FILE = './DynDNSLogClient.json'
PID_ROOT_PATH = '/var/run/DynDNSLogClient.pid'
PID_USER_PATH = 'DynDNSLogClient.pid'
DEBUG = False
TERMINATE = False
MAX_MESSAGES_PER_CALL = 50
# Jan 1, 2013, 00:00:00 GMT
FIRST_VALID_TS = 1356998400
# Dec 31, 2050 23:49:59
LAST_VALID_TS = 2556104399

# enums for message header
CUSTID = 0
LABEL = 1
TIMESTAMP = 2

"""
Class that actually monitors the message queue and handle the data
"""
class MonitorQueue(object):
    """
    Initialize the class
    """
    def __init__(self, config, dLogger, dirs, pidPath):
        self.queues = []
        self.config = config
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/dev/tty'
        self.pidfile_path = pidPath
        self.pidfile_timeout = 5
        self.dLogger = dLogger
        self.dirs = dirs
        # Timestamps
        self.currentTS = None
        self.prevTS = None
        self.prevTSCutoff = None
        # File write objects
        self.currentFiles = {}
        self.prevFiles = {}
        self.lateFiles = {}

    """
    Configure the messages queues
    """
    def configureMQ(self):
        for url in self.config['queueurls']:
            queueDef = {}
            connection = IronMQ(host=url,
                                project_id=self.config['projectid'],
                                token=self.config['token'],
                                protocol=self.config['queueprotocol'],
                                port=self.config['queueport'],
                                api_version=self.config['apiversion'],
                                config_file=None)

            # Get the queue
            queue = connection.queue(self.config['queuename'])

            # Save our stuff
            queueDef['url'] = url
            queueDef['connection'] = connection
            queueDef['queue'] = queue
            self.queues.append(queueDef)

    """
    Move old staging files to pickup
    """
    def moveOldFiles(self):
        # Start by scanning the staging directory for existing files
        for filepath in glob.glob(self.dirs['staging'] + '*.log'):
            filename = os.path.basename(filepath)
            # Strip ".log" for ease of parsing the name
            work = filename[:-4]
            work = work.split('_')
            if len(work) < 2:
                continue

            # Convert the date-time field to a timestamp for comparison
            try:
                epoch = self.convertDateStringToEpoch(work[1]) - self.config['period']
            except:
                # If an invalid file name, ignore it
                continue

            # Now see if we have to move it.  Ones that we don't move should be put in the apppropriate fileDict
            # Late files first.  Timestamps must match
            if len(work) > 2:
                # If the 3rd section doesn't contain "late", no idea what this is.
                if work[2] != 'late':
                    continue
                if epoch != self.currentTS:
                    os.rename(filepath, self.dirs['pickup'] + filename)
                    continue
                else:  # Add to the "late" fileDict
                    self.getFileObj(self.lateFiles, work[0], epoch, True)
                    continue

            # See if the rest are current, previous, or old
            # Current. getFileObj will recreate the name and open the file for appending
            if epoch == self.currentTS:
                self.getFileObj(self.currentFiles, work[0], epoch)
                continue
            # Previous. getFileObj will recreate the name and open the file for appending
            if epoch == self.prevTS:
                self.getFileObj(self.prevFiles, work[0], epoch)
                continue

            # Old, need to move it
            os.rename(filepath, self.dirs['pickup'] + filename)

        return

    """
    This function converts the file name dates to epoch
    """
    def convertDateStringToEpoch(self, datestr):
        try:
            year = int(datestr[:4])
            mon = int(datestr[4:6])
            day = int(datestr[6:8])
            hour = int(datestr[-4:-2])
            minute = int(datestr[-2:])
            epoch = (datetime.datetime(int(year), int(mon), int(day), int(hour),
                                   int(minute)) - datetime.datetime(1970, 1, 1)).total_seconds()
        except:
            raise

        return int(epoch)

    """
    Calculate the timestamps and closing timestamps
    """
    def checkCloseFileTimestamps(self):
        current = now = int(time.time())
        mod = current % self.config['period']
        current -= mod

        # First time?
        if self.currentTS is None:
            self.currentTS = current
            self.prevTS = current - self.config['period']
            self.prevTSCutoff = current + self.config['timetowait']
            return

        # Check to see if we've waited long enough to close the PREVIOUS time period
        if now > self.prevTSCutoff:
            # Close previous period files
            for zone, fileObj in self.prevFiles.iteritems():
                fileObj.moveFile(False)
            self.prevFiles = {}

        # Check to see if it's time to update the CURRENT timestamp
        if current != self.currentTS:
            # Close LATE files
            for zone, fileObj in self.lateFiles.iteritems():
                fileObj.moveFile(True)
            self.lateFiles = {}

            # Save the current period file objects to the previous period dict
            self.prevFiles = self.currentFiles

            # Reinitialize the current period dict
            self.currentFiles = {}

            # Set new timestamp values
            self.prevTS = self.currentTS
            self.prevTSCutoff = current + self.config['timetowait']
            self.currentTS = current

    """
    Get or create the file object
    """
    def getFileObj(self, fileDict, label, timestamp, late=False):
        # See if we have a file object
        try:
            fileObj = fileDict[label]
        except:
            fileObj = FileWriter(self.config, self.dirs, self.dLogger)
            fileObj.createFile(label, timestamp, late)
            fileDict[label] = fileObj
        return fileObj

    """
    Our run loop
    """
    def run(self):
        global TERMINATE
        if not DEBUG:
            self.dLogger.logger.info("DynDNSLogClient daemonized")
        self.dLogger.logger.info(
            "Connecting to queue " + self.config['queuename'] + ' at ' + self.config['queueurls'][0])

        # Configure and log in to all endpoints
        self.configureMQ()

        # Metric object
        metrics = Metrics(self.dLogger)

        # Tag first run through
        bFirst = True

        # Flag for if we got data
        bGotData = False

        # Get the messages
        while True:
            # Write metrics
            if time.time() - metrics.lastWrite >= 300:
                metrics.Output()
            # Try all queues endpoints - they may have failed over
            for queueDef in self.queues:
                # See if it's time to close and move files
                self.checkCloseFileTimestamps()

                # Log rollover?
                self.dLogger.checkRollover()

                # If first time through check for old files
                if bFirst:
                    bFirst = False
                    self.moveOldFiles()

                # Get the message
                # max = number of messaegs to get at once
                # timeout = time in secs if not deleted to go back on the queue (we do this in the same call)
                # wait = time to long poll for messages
                # delete - remove the message after we get it
                response = queueDef['queue'].reserve(max=MAX_MESSAGES_PER_CALL, timeout=30, wait=0, delete=True)

                # Metric
                metrics.Add(metrics.MSG_CALLS, 1)
                recvd = len(response['messages'])
                if recvd > 0:
                    metrics.Add(metrics.MSG_CALLS_WITH_DATA, 1)
                    metrics.Add(metrics.MSG_RECVD, recvd)

                # Write them to the appropriate file
                # Arrivals too late for lastPeriod are grouped into the "late" files
                for message in response['messages']:
                    bGotData = True
                    metrics.Add(metrics.KBYTES_RECV, len(message['body']) / 1024)
                    payload = message['body']
                    # Compressed data?
                    if self.config['compression']:
                        try:
                            decoded = base64.decodestring(message['body'])
                        except:
                            self.dLogger.logger.error("Received an invalid base64 encoded message")
                            continue
                        try:
                            payload = snappy.uncompress(decoded)
                        except:
                            e = sys.exc_info()[0]
                            print( "Error: %s" % e )
                            self.dLogger.logger.error("Unable to decompress message")
                            continue

                    # Extract the key and the log lines
                    index = str(payload).find('}')
                    if index == -1:
                        self.dLogger.logger.warn("Received a message with an invalid header")
                        continue
                    key = str(payload)[1:index]
                    loglines = str(payload)[index + 1:]
                    keys = key.split(',')
                    # Get the key fields
                    try:
                        if len(keys) != 3:
                            raise
                        label = keys[LABEL]
                        timestamp = int(keys[TIMESTAMP])
                        # Make sure that the timestamp is sane
                        if timestamp < FIRST_VALID_TS or timestamp > LAST_VALID_TS:
                            self.dLogger.logger.warn("Received a message with an invalid timestamp: " + str(timestamp))
                            continue
                    except:
                        self.dLogger.logger.warn("Received a message with an invalid header")
                        continue

                    metrics.Add(metrics.KBYTES_WRITTEN, len(loglines) / 1024)

                    # Where do these lines go?  First check the timestamp.
                    # Current
                    if timestamp >= self.currentTS:
                        metrics.Add(metrics.CURRENT_KB, len(loglines) / 1024)
                        fileObj = self.getFileObj(self.currentFiles, label, self.currentTS)
                        fileObj.writeFile(loglines)
                        continue

                    # Previous?  We must be within the "previous" grace period, and it must be in the previous hour
                    current = int(time.time())
                    if self.prevTSCutoff >= current and timestamp >= self.prevTS:
                        metrics.Add(metrics.PREV_KB, len(loglines) / 1024)
                        fileObj = self.getFileObj(self.prevFiles, label, self.prevTS)
                        fileObj.writeFile(loglines)
                        continue

                    # It's late
                    metrics.Add(metrics.LATE_KB, len(loglines) / 1024)
                    fileObj = self.getFileObj(self.lateFiles, label, self.currentTS, True)
                    fileObj.writeFile(loglines)
                    continue

            # Time to terminate the daemon?
            if TERMINATE:
                # Close all files
                self.dLogger.info("Closing all staging files")
                for zone, fileObj in self.currentFiles.iteritems():
                    fileObj.closeFile()
                for zone, fileObj in self.prevFiles.iteritems():
                    fileObj.closeFile()
                for zone, fileObj in self.lateFiles.iteritems():
                    fileObj.closeFile()
                sys.exit(0)

            # IF we didn't get data, wait so we don't needlessly pummel the API
            if not bGotData:
                time.sleep(5)

            # Reset flag
            bGotData = False


"""
Replicates 'mkdir -p'
"""
def mkdirp(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


"""
Handles the term signal
"""
def sigterm_handler(signalcaught, frame):
    global TERMINATE
    TERMINATE = True


"""
Main
"""
def main():
    global DEBUG

    # Any args?
    if len(sys.argv) == 1:
        print "\n" + unichr(169) + " Dyn, Inc. 2016"
        print "DynDNSLogClient - subscribe and process streaming DNS log data\n"
        print "Usage: ./DynDNSLogClient.py debug - run in console mode"
        print "       sudo ./DynDNSLogClient.py start - run in daemon mode"
        print "       sudo ./DynDNSLogClient.py stop - stop running daemon"
        print "       sudo ./DynDNSLogClient.py restart - restart daemon"
        sys.exit(0)

    # Debug mode?
    if sys.argv[1] == "debug":
        DEBUG = True

    script_path = os.path.dirname(os.path.realpath(__file__))
    config_file = script_path
    config_file += '/' + DEFAULT_CONFIG_FILE

    # Are we running as root?  If yes, PID_ROOT_PATH is fine.  Otherwise we need a user path.
    pidPath = PID_ROOT_PATH
    if os.geteuid() != 0:
        pidPath = script_path + '/run'
        mkdirp(pidPath)
        pidPath += '/' + PID_USER_PATH

    # Read and parseconfiguration
    config = Configuration(config_file)

    # Get a logger
    dLogger = Logger()

    # Print processed configuration for debugging
    if DEBUG:
        for key, value in config.QueueConfig.iteritems():
            print key, value

    # Ensure that our destination directories exist and that we can write to them
    dirs = {}
    dest = config.QueueConfig['destination']
    if dest[-1] != '/':
        dest += '/'
    dirs['staging'] = dest + 'staging/'
    dirs['pickup'] = dest + 'pickup/'

    # Create them all
    for directory, path in dirs.iteritems():
        mkdirp(path)

    # Make sure we capture a kill    
    signal.signal(signal.SIGTERM, sigterm_handler)

    # Application/daemon stuff
    app = MonitorQueue(config.QueueConfig, dLogger, dirs, pidPath)
    if DEBUG:
        app.run()
    else:
        dLogger.logger.info("Daemonizing . . .")
        daemon_runner = runner.DaemonRunner(app)
        daemon_runner.daemon_context.files_preserve = [dLogger.handler.stream]
        daemon_runner.do_action()

# Main!
if __name__ == '__main__':
    main()
