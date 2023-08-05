import sys
from collections import OrderedDict
from uuid import uuid4

from tornado.ioloop import IOLoop
from tornado import gen

from .checker import Checker


class SystemsMonitor(object):
    """Monitors multiple systems for yes/no status."""
    def __init__(self, loop=None):
        self.checkers = OrderedDict()
        self.categories = []
        self.loop = loop or IOLoop.instance()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if 'win' in sys.platform:
            self.shutdown(wait=False)
        else:
            self.terminate()

    def close(self):
        pass

    def _add_checker(self, checker, name, description, category, warn):
        self.checkers[name] = {
            'checker': checker,
            'name': name,
            'description': description,
            'category': category,
            'warn': warn
        }
        if category not in self.categories:
            self.categories.append(category)

    def register(self, checker, description='', category='Systems',
                 warn=False):
        """Register a new system checker.

        :param syscheck.Checker checker:
        :param str description:
        :param str category:
        :param bool warn: flag as a warning when the check returns
                          False

        """
        assert isinstance(checker, Checker)
        assert isinstance(description, str)
        assert isinstance(category, str)
        name = str(uuid4())
        if description == '':
            description = checker.__class__.__name__
        self._add_checker(checker, name, description, category, warn)

    def register_category(self, category, checkers):
        """Register a group of checkers all belonging to one
        category.

        :param str category: name of the category
        :param list checkers: list tuples containing Checkers and
                              (optionally) descriptions and warning
                              status

        Example::

          monitor.register_category(
              'Category',
              [
                  (DummyChecker(), 'First dummy checker'),
                  (DummyChecker(), 'Second dummy checker', True)
              ]
          )

        """
        assert isinstance(category, str)
        assert isinstance(checkers, (tuple, list))
        for checker in checkers:
            if not isinstance(checker, (tuple, list)):
                raise RuntimeError(
                    "Register categories with tuples: (checker, description)")
            description = checker[0].__class__.__name__ if len(checker) is 1 else checker[1]
            warn = checker[-1] if len(checker) is 3 else False
            self.register(checker[0], description, category, warn)

    def get_categories(self):
        """Return a list of unique checker categories."""
        return self.categories

    def jsonize(self):
        """Return a JSON-serializable version of the ``checkers``
        dict, i.e., remove the Checker object from each item.

        """
        checkers = OrderedDict()
        for checker in self.checkers.keys():
            current = self.checkers[checker]
            checkers[current['name']] = {
                key: current[key] for key in current if key != 'checker'
            }
        return checkers

    @gen.coroutine
    def _check_one(self, checker):
        result = yield gen.maybe_future(checker.check())
        raise gen.Return(result)

    @gen.coroutine
    def check(self, timeout=5.0):
        """Check the status of all systems.

        :param float timeout: time before assuming a system is down in
                              seconds.

        """
        checkers = [self.checkers[name]['checker'] for name in self.checkers]
        waiter = gen.WaitIterator(*[self._check_one(checker) for checker in checkers])
        statuses = [False]*len(checkers)
        while not waiter.done():
            try:
                result = yield waiter.next()
            except Exception as error:
                result = False
                print("Error {} from {}".format(error, waiter.current_future))
            statuses[waiter.current_index] = result
        raise gen.Return(statuses)
