import time
import os

DEBUG=True

"""
Log file writer
"""
class FileWriter(object):
    """
    Initialize the class
    """
    def __init__(self, config, dirs, dLogger):
        self.config = config
        self.dirs = dirs
        self.dLogger = dLogger
        self.handle = None
        self.filepath = None
        self.filename = None
        self.pickuppath = None

    """
    Create the proper log file name
    """
    def makeFilePath(self, label, timestamp, late=False):
        tstruct = time.gmtime(timestamp + self.config['period'])
        tslabel = str(tstruct.tm_year) + str(tstruct.tm_mon).zfill(2) + \
                  str(tstruct.tm_mday).zfill(2) + '-' + str(tstruct.tm_hour).zfill(2) + str(tstruct.tm_min).zfill(2)
        if late:
            self.filename = label + '_' + tslabel + '_late.log'
        else:
            self.filename = label + '_' + tslabel + '.log'
        self.filepath = self.dirs['staging'] + self.filename
        self.pickuppath = self.dirs['pickup'] + self.filename

        return self.filepath

    """
    Create a file
    """
    def createFile(self, label, timestamp, late):
        self.makeFilePath(label, timestamp, late)
        # Open in append mode.  We don't automatically move staging files on close.
        # because if we are restarted in the same time period we would recreate a file
        # with the same name.
        self.handle = open(self.filepath, 'a')
        if DEBUG:
            print "Creating file", self.filepath
        return self.handle

    """
    Write messages to file
    """
    def writeFile(self, payload):
        return self.handle.write(payload)

    """
    Move the file from the staging to the pickup directory
    """
    def moveFile(self, late=False):
        if DEBUG:
            print "moveFile", self.filepath
        self.closeFile()
        if DEBUG:
            print "Closing ", self.filepath
            print "Moving ", self.filepath, "to", self.pickuppath

        os.rename(self.filepath, self.pickuppath)

    """
    Close the file
    """
    def closeFile(self):
        self.handle.close()

