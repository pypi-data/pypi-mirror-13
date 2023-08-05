"""Web interface for brush."""

import os.path
import logging
import time
from concurrent.futures import ThreadPoolExecutor
import json

from tornado.web import Application, RequestHandler, MissingArgumentError
from tornado import gen
from tornado.concurrent import run_on_executor
from tornadose.handlers import EventSource
from tornadose.stores import QueueStore
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from .db import get_data_since, get_data_between
from .stores import store

logger = logging.getLogger('web')

base_dir = os.path.dirname(__file__)
default_static_path = os.path.abspath(
    os.path.join(base_dir, 'static'))
template_path = os.path.abspath(
    os.path.join(base_dir, 'templates'))

engine = None


class Publisher(QueueStore):
    """Slightly-modified QueueStore to hold last data in a manner
    accessible for REST queries.

    """
    def initialize(self):
        super(Publisher, self).initialize()
        self.data = None

    @gen.coroutine
    def submit(self, message):
        self.data = message
        yield self.messages.put(message)

publisher = Publisher()


class MainHandler(RequestHandler):
    def get(self):
        """Main page for displaying real-time data."""
        self.render('index.html')


class DataHandler(RequestHandler):
    executor = ThreadPoolExecutor(max_workers=4)

    def initialize(self, engine):
        self.uri = engine.url

    @run_on_executor
    def get_data(self, start, stop):
        """Retrieve the data using a background thread."""
        engine = create_engine(self.uri)
        try:
            if stop is None:
                data = get_data_since(engine, start)
            else:
                if stop < start or start > time.time():
                    data = 400
                data = get_data_between(engine, start, stop)
            data.pop('timestamp')
        except Exception as e:
            raise e
        finally:
            engine.dispose()
        return data

    @gen.coroutine
    def get(self):
        """Get data starting from the timestamp ``start`` up until the
        timestamp ``stop``. These timestamps should be passed as query
        arguments in the ``GET`` request, though only ``start`` is
        required. If ``stop`` is not given, all data starting from
        ``start`` is returned.

            http://localhost:8090/data?start=1449142201

        .. note:: Python uses seconds whereas Javascript uses
                  milliseconds.

        """
        try:
            start = float(self.get_query_argument('start'))
        except MissingArgumentError:
            self.send_error(400)
            return
        try:
            stop = float(self.get_query_argument('stop'))
        except MissingArgumentError:
            stop = None
        try:
            data = yield self.get_data(start, stop)
            if data == 400:
                self.send_error(400)
        except Exception:
                self.send_error(400)
        else:
            self.write(data)


class QueryHandler(RequestHandler):
    def get(self, key):
        """Return the most recent value for the requested key."""
        try:
            logger.debug(publisher.data)
            value = json.loads(publisher.data)[key]
            self.write({
                key: value,
                'error': None
            })
        except KeyError:
            self.write({'error': 'No such key'})


def make_app(engine_, prefix=None, static_path=default_static_path,
             debug=False):
    """Initialize the Tornado web app.

    :param str prefix: URL prefix for routing
    :param bool debug: enable debug mode if True

    """

    # This is a horrible way to do things... It would probably be
    # better to somehow move the engine into the db module.
    assert isinstance(engine_, Engine)
    global engine
    engine = engine_

    handlers = [
        ['/', MainHandler],
        ['/stream', EventSource, {'store': publisher}],
        ['/data', DataHandler, dict(engine=engine)],
        ['/query/(.*)', QueryHandler]
    ]
    if prefix:
        if prefix[0] != '/':
            prefix = '/' + prefix
        for handler in handlers:
            route = handler[0]
            if route == '/':
                handler[0] = prefix
            else:
                handler[0] = prefix + route

    app = Application(
        handlers,
        template_path=template_path,
        static_path=static_path,
        debug=debug
    )
    return app
