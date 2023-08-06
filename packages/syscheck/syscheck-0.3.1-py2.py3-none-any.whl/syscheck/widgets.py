from tornado.web import UIModule


class Category(UIModule):
    def render(self, monitor, category, columns):
        """Render a category of checkers.

        :param syscheck.monitor.SystemsMonitor monitor:
        :param str category: category name

        """
        return self.render_string('module-category.html',
                                  checkers=monitor.checkers,
                                  category=category,
                                  columns=columns)
