"""Application module."""

import jinja2
import logging

from werkzeug import exceptions

from webgears import routing
from webgears import views


class Application(object):
    """Base application."""

    rule_maps = []

    def __init__(self, templates_dir=None):
        """Initializer."""
        self._logging = self._init_logging()

        self._router = self._init_router()
        self._jinja_env = self._init_templates_system(templates_dir)

        self._views = self._init_views(self._jinja_env)

    def __call__(self, environ, start_response):
        """Dispatch WSGI request."""
        request = views.Request(environ)

        router_adapter = self._router.bind_to_environ(request.environ)
        try:
            endpoint, values = router_adapter.match()
        except exceptions.HTTPException as exception:
            return exception(environ, start_response)
        else:
            view = self._views[endpoint]

        try:
            response = view.handle_request(request, router_adapter, values)
        except exceptions.HTTPException as exception:
            return exception(environ, start_response)
        except Exception as exception:
            self.logger.exception(exception)
            return exceptions.ServiceUnavailable(environ, start_response)
        else:
            return response(environ, start_response)

    def _init_router(self):
        """Initialize application router."""
        router = routing.Router()
        for rules_map in self.__class__.rule_maps:
            router.bind_rules_map(rules_map)
        return router

    def _init_templates_system(self, templates_dir):
        """Initialize application templates system."""
        return jinja2.Environment(
            loader=jinja2.FileSystemLoader(templates_dir))

    def _init_views(self, jinja_env):
        """Initialize application views."""
        return dict((rule.endpoint, rule.view_provider(jinja_env=jinja_env))
                    for rule in self._router.iter_rules())

    def _init_logging(self):
        """Initialize application loggign."""
        logging.basicConfig()
        return logging.getLogger('webgears')


__all__ = (
    'Application',
)
