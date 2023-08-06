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
        # Init router
        self.router = routing.Router()
        for rules_map in self.__class__.rule_maps:
            self.router.bind_rules_map(rules_map)

        # Init Jinja2
        self.jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(templates_dir))

        # TODO: setup logging properly
        logging.basicConfig()
        self.logger = logging.getLogger('webgears')

    def __call__(self, environ, start_response):
        """Dispatch WSGI request."""
        request = views.Request(environ)

        router_adapter = self.router.bind_to_environ(request.environ)
        try:
            rule, values = router_adapter.match(return_rule=True)
        except exceptions.HTTPException as exception:
            return exception(environ, start_response)
        else:
            view = rule.view_provider(request=request,
                                      router_adapter=router_adapter,
                                      jinja_env=self.jinja_env)

        try:
            response = view.handle_request(**values)
        except exceptions.HTTPException as exception:
            return exception(environ, start_response)
        except Exception as exception:
            self.logger.exception(exception)
            return exceptions.ServiceUnavailable(environ, start_response)
        else:
            return response(environ, start_response)


__all__ = (
    'Application',
)
