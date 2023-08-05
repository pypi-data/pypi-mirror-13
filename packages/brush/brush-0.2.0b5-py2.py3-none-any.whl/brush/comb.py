"""XMLRPC data acquisition from Menlo frequency combs."""

from abc import ABCMeta, abstractmethod
from collections import defaultdict
import time
import random
import six
from six.moves.xmlrpc_client import ServerProxy


class MenloCombError(Exception):
    """Generic Menlo comb errors."""


@six.add_metaclass(ABCMeta)
class BaseFrequencyComb(object):
    """Abstract base class for frequency combs. This allows for real
    and simulated combs for testing.

    """
    @abstractmethod
    def get_data(self, keys):
        """Get data corresponding to the passed keys."""

    @abstractmethod
    def get_version(self):
        """Return the version number of the control software."""

    def __getitem__(self, key):
        """Shortcut for getting one data entry without timestamp."""
        result = self.get_data([key])
        return result[key]


class DummyFrequencyComb(BaseFrequencyComb):
    """Simulated frequency comb for testing purposes."""
    def __init__(self):
        """Create an empty metadata dict to be filled in later."""
        default = lambda: dict(type='double', description='Dummy test case')
        self.metadata = defaultdict(default)
        self.metadata['counter2.freq']['type'] = 'double'
        self.metadata['counter2.freq']['description'] = 'Counter channel 2 frequency'

    def get_data(self, keys):
        """Return random numbers."""
        data = {key: random.random() for key in keys}
        data['timestamp'] = time.time()
        return data

    def get_version(self):
        return '1.0.0_Dummy'

    def keys(self):
        return self.metadata.keys()


class FrequencyComb(BaseFrequencyComb):
    """Class for communicating with a Menlo frequency comb."""
    def __init__(self, host, port=8123, user=None, password=None):
        """Opens a connection to the remote comb server."""
        url = 'http://'
        if user is not None:
            assert isinstance(user, six.string_types)
            url += user
        if password is not None:
            assert isinstance(password, six.string_types)
            url += ':' + password
        url += '@'
        assert isinstance(host, six.string_types)
        url += host + ':' + str(port) + '/RPC2'

        self.server = ServerProxy(url)
        self._keys = self.server.data.getInfo().keys()
        data_info = self.server.data.getInfo()
        self.metadata = {
            key: {
                'type': data_info[key][0],
                'description':  data_info[key][1]
            } for key in self._keys
        }

    def get_data(self, keys):
        """Return a several data points."""
        if not isinstance(keys, list):
            raise MenloCombError('keys must be a list.')
        for key in keys:
            if key not in self._keys:
                raise MenloCombError('Invalid data parameter: %s.' % key)
        t = self.server.data.last_timestamp() - 0.01
        data = self.server.data.query(t, keys)
        timestamp = list(data.keys())[0]
        data = data.pop(timestamp)
        result = {'timestamp': float(timestamp)}
        for key in keys:
            result[key] = data[key]
        return result

    def keys(self):
        """Retun the list of keys."""
        return self._keys

    def get_version(self):
        """Return the control software version."""
        return self.server.hello()


def open_connection(config):
    """Open a connection to a comb system."""
    password = config['xmlrpc']['password'] or ''
    try:
        comb = FrequencyComb(
            str(config['xmlrpc']['host']),
            user=str(config['xmlrpc']['user']),
            password=str(password))
    except:
        print("Error connecting to comb. Running in offline mode.")
        comb = DummyFrequencyComb()
    return comb
