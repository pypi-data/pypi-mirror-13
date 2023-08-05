"""Module containing the 'sweep' functionality, i.e., periodic polling
and logging of data.

"""

import logging
import signal
import json
from datetime import datetime

from tornado import gen
from tornado.locks import Event

from . import db
from .comb import DummyFrequencyComb, FrequencyComb
from .web import make_app, publisher
from .stores import store

logger = logging.getLogger('brush')

try:
    import msgpack
    import redis
except ImportError:
    logger.warning('msgpack and/or redis not found.'
                   ' Will not try to write to Redis.')
    msgpack = None
    redis = None


def sleep_time():
    """Time to sleep when the comb is not locked. Starts at a second,
    then increases up to a minute.

    """
    t = 1
    times = {1: 5, 5: 10, 10: 10}
    while True:
        yield t
        t = times[t]


class Sweep(object):
    def __init__(self, comb, config, args):
        assert isinstance(comb, (DummyFrequencyComb, FrequencyComb))
        self.comb = comb
        self.offline = args.offline

        # Check keys and ensure that offset, rep rate, and locked status
        # are always checked. Note that lb1/lb2 indicate rep rate/CEO
        # lockbox statuses.
        self.config = config
        if 'keys' not in config:
            self.config['keys'] = args.keys.split(',')
        for key in ['offset.freq', 'reprate.freq', 'system.locked',
                    'counter0.freq', 'counter1.freq',
                    'lb1.status', 'lb2.status']:
            if key not in config['keys']:
                self.config['keys'].append(key)

        # Initialize databases
        self._init_sql(args.uri)
        self._init_redis()

        # Start the web server
        self.done = Event()
        self.app = make_app(self.engine, prefix=args.prefix, debug=args.debug)
        self.app.listen(args.port)
        signal.signal(signal.SIGINT, lambda num, frame: self.done.set())
        logger.info('Listening on port ' + str(args.port))

    def _init_sql(self, uri):
        """Initialize the SQL database."""
        dtypes = []
        for key in self.config['keys']:
            try:
                dtypes.append(self.comb.metadata[key]['type'])
            except KeyError:
                logger.warning('Invalid key in passed configuration: ' + key)
                self.config.pop(key)
        if uri:
            engine, table = db.create_sql_table(uri, self.config['keys'], dtypes)
        elif 'sql' in self.config:
            engine, table = db.create_sql_table(
                self.config['sql']['uri'], self.config['keys'], dtypes)
        else:
            raise RuntimeError("No database URI specified!")

        self.engine = engine
        self.table = table

    def _init_redis(self):
        """Connect to redis if applicable."""
        self.redis = None
        if 'redis' in self.config and redis is not None:
            try:
                rconf = self.config['redis']
                host = rconf['host']
                port = 6379 if 'port' not in rconf else rconf['port']
                password = None if 'password' not in rconf else rconf['password']
                self.redis = redis.StrictRedis(
                    host=host, port=port, password=password)
            except Exception:
                logger.error(
                    'Error configuring or connecting to Redis. Disabling.')

    def jsonize(self, data):
        """Return a JSONized version of data."""
        jsonized = data.copy()
        jsonized.pop('timestamp')
        timestamp = jsonized.pop('unix_timestamp')
        jsonized['timestamp'] = timestamp
        return json.dumps(jsonized)

    @gen.coroutine
    def run(self):
        """Periodically polls the comb server for data."""
        # Start polling
        last_timestamp = None
        while not self.done.is_set():
            data = self.comb.get_data(self.config['keys'])
            timestamp = datetime.fromtimestamp(data['timestamp'])
            unix_timestamp = data['timestamp']
            locked = data['system.locked']

            if timestamp == last_timestamp:
                yield gen.sleep(0.01)
                continue
            last_timestamp = timestamp

            data['timestamp'] = timestamp
            data['unix_timestamp'] = unix_timestamp
            data = {key.replace('.', '_').lower(): data[key] for key in data}
            yield publisher.submit(self.jsonize(data))

            # Don't record data if the comb isn't locked. It still gets
            # pushed to subscribed listeners so that things like rep
            # rate can be adjusted.
            if locked:
                db.insert_row(self.engine, self.table, data)

            store.append(data)

            if self.redis is not None:
                data.pop('timestamp')
                self.redis.set('brush', msgpack.dumps(data))
            if self.offline:
                yield gen.sleep(1)
