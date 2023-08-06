"""Web-based interface for monitoring system statuses."""

from __future__ import division

import os.path as osp
import logging
import json

from tornado import ioloop, gen
from tornado.web import Application, RequestHandler
from tornado.options import define, options
from tornadose.stores import QueueStore
from tornadose.handlers import EventSource

from . import widgets
from .monitor import SystemsMonitor

logger = logging.getLogger(__name__)

define('period', default=5, help='Approximate time between checks in seconds')
define('port', default=8999, help='HTTP port to serve on')
define('debug', default=False, help='Enable debug mode')
define('title', default='Systems Check', help='Page title to use')
define('url_prefix', default='', help='URL subdir')
define('columns', default=2, help='Number of columns for status display')


class MainHandler(RequestHandler):
    def initialize(self, monitor, title='Systems Check'):
        assert isinstance(monitor, SystemsMonitor)
        assert isinstance(title, str)
        self.monitor = monitor
        self.title = title

    def get(self):
        """Returns the main page for showing system status."""
        self.render('index.html',
                    title=self.title,
                    monitor=self.monitor,
                    categories=self.monitor.categories,
                    checkers=json.dumps(self.monitor.jsonize()),
                    columns=int(12/options.columns))


class StatusCheckHandler(RequestHandler):
    def get(self):
        """Returns the current status of all checkers."""
        self.write(CheckerApp.statuses)


class CheckerApp(Application):
    """Tornado web app for handling status check requests.

    :param SystemsMonitor monitor: ``SystemsMonitor`` instance
    :param list extra_handlers: additional ``RequestHandler`` specs
    :param title: title for the main page

    """
    statuses = None

    def __init__(self, monitor, extra_handlers=None,
                 title=options.title, *args, **kwargs):
        assert isinstance(title, str)
        self.monitor = monitor
        self.store = QueueStore()

        handlers = [
            [r'/', MainHandler, dict(monitor=monitor, title=options.title)],
            [r'/status', StatusCheckHandler],
            [r'/stream', EventSource, dict(store=self.store)]
        ]

        if options.url_prefix != '':
            prefix = options.url_prefix
            if prefix[0] != '/':
                prefix = '/' + prefix
            for handler in handlers:
                handler[0] = prefix + handler[0]
                if len(handler[0]) > 1:
                    handler[0].strip('/')

        if extra_handlers:
            handlers += extra_handlers

        self.started = False

        dirname = osp.dirname(__file__)
        static_path = osp.abspath(osp.join(dirname, 'static'))
        template_path = osp.abspath(osp.join(dirname, 'templates'))

        super(CheckerApp, self).__init__(
            handlers, *args, debug=options.debug,
            static_path=static_path, template_path=template_path,
            ui_modules=widgets,
            **kwargs)

    @gen.coroutine
    def _check_and_push(self):
        """Check all statuses and push the results with a
        websocket.

        """
        logger.debug('Checking statuses...')
        statuses = yield self.monitor.check()
        CheckerApp.statuses = {
            self.monitor.checkers[key]['name']: statuses[i] for i, key in enumerate(self.monitor.checkers.keys())}
        self.store.submit(json.dumps(self.statuses))

    def start_checking(self, period=options.period):
        """Initialize checking all checkers. This method is called
        automatically if using ``app.listen(port)`` to start the
        app. It only needs to be explicitly called if running through
        a specially configured ``HTTPServer`` instance.

        """
        callback = ioloop.PeriodicCallback(self._check_and_push, period*1000)
        callback.start()
        self.started = True

    def listen(self, port, address='', **kwargs):
        """Start listening on the given port."""
        if not self.started:
            self.start_checking()
        logger.info("Listening on port {}".format(options.port))
        super(CheckerApp, self).listen(port, address, **kwargs)
