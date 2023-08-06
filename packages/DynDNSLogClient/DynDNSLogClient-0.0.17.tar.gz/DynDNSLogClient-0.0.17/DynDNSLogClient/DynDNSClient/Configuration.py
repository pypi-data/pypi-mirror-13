import json

"""
We use an instance of this to parse our configuration file
"""
class Configuration(object):
    """
    Initialization
    """
    def __init__(self, config_file):
        self.config_file = config_file
        self.QueueConfig = {}
        self.read_config()

    """
    Read in and parse the config file
    """
    def read_config_file(self):

        if self.config_file is None:
            print "No conf file specified"
            raise Exception

        # Open the file and read it
        try:
            file_handle = open(self.config_file, "r")

        except IOError:
            print "Could not open conf file: %s" % self.config_file
            raise IOError

        file_data = file_handle.read()
        file_handle.close()

        # Decode the json data
        try:
            decoded = json.loads(file_data)

        except ValueError:
            print "Invalid JSON in %s" % self.config_file
            raise ValueError

        # Make sure the top level is a dictionary
        if not isinstance(decoded, dict):
            print "Config file top level structure must be a hash. Currently: %s" % str(type(decoded))
            raise Exception

        return decoded

    """
    Get our settings
    """
    def read_config(self):

        # Read in the config file
        config = self.read_config_file()

        # Customer queue name
        try:
            self.QueueConfig['queuename'] = config.get('QueueName')
        except ValueError:
            print "'QueueName' is required"
            raise ValueError

        # Dyn project ID
        try:
            self.QueueConfig['projectid'] = config.get('ProjectID')
        except ValueError:
            print "'ProjectID' is required"
            raise ValueError

        # Customer token
        try:
            self.QueueConfig['token'] = config.get('Token')
        except ValueError:
            print "'Token' is required"
            raise ValueError

        # URLs for queue, JSON array
        try:
            self.QueueConfig['queueurls'] = config.get('QueueURLs')
        except ValueError:
            print "'QueueURLs' is required"
            raise ValueError

        # Queue protocol - should always be https
        try:
            self.QueueConfig['queueprotocol'] = config.get('QueueProtocol')
        except ValueError:
            print "'QueueProtocol' is required"
            raise ValueError

        # Queue port - should always be 443
        try:
            self.QueueConfig['queueport'] = int(config.get('QueuePort'))
        except ValueError:
            print "'QueuePort' is required"
            raise ValueError

        # API version
        try:
            self.QueueConfig['apiversion'] = int(config.get('APIVersion'))
        except ValueError:
            print "'APIVersion' is required"
            raise ValueError

        # Destination directory
        try:
            self.QueueConfig['destination'] = config.get('DestinationDirectory')
        except ValueError:
            print "'DestinationDirectory' is required"
            raise ValueError

        # Log period - 5 minutes, hourly, or daily.  Convert to seconds.
        try:
            period = config.get('LogPeriod')
            if period % 5 != 0:
                raise ValueError
            self.QueueConfig['period'] = period * 60
        except ValueError:
            print "'LogPeriod' is required and must be a multiple of 5"
            raise ValueError

        # Time to wait before closing the period.  Convert to seconds.
        try:
            self.QueueConfig['timetowait'] = int(config.get('TimeToWaitMinutes')) * 60
            if self.QueueConfig['timetowait'] > self.QueueConfig['period']:
                raise ValueError
        except ValueError:
            print "'TimeToWaitMinutes' is required, must be an integer, and must be less than the 'LogPeriod'"
            raise ValueError

        # Destination directory
        try:
            self.QueueConfig['logmetrics'] = config.get('LogPerformanceMetrics')
        except ValueError:
            self.QueueConfig['logmetrics'] = False

        try:
            self.QueueConfig['compression'] = config.get('UseCompression')
        except ValueError:
            self.QueueConfig['compression'] = True


