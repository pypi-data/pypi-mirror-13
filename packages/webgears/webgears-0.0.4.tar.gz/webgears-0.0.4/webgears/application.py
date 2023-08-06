"""Application module."""

from werkzeug import exceptions

from webgears import routing
from webgears import views


class Application(object):
    """Base application."""

    rule_maps = []

    def __init__(self):
        """Initializer."""
        self.router = routing.Router()
        for rules_map in self.__class__.rule_maps:
            self.router.bind_rules_map(rules_map)

    def __call__(self, environ, start_response):
        """Dispatch WSGI request."""
        request = views.Request(environ)

        adapter = self.router.bind_to_environ(request.environ)
        try:
            rule, values = adapter.match(return_rule=True)
        except exceptions.HTTPException as exception:
            return exception(environ, start_response)
        else:
            view = rule.view_provider(request)

        try:
            response = view.handle_request(**values)
        except exceptions.HTTPException as exception:
            return exception(environ, start_response)
        except Exception as exception:
            # TODO: log exception
            return exceptions.ServiceUnavailable(environ, start_response)
        else:
            return response(environ, start_response)


__all__ = (
    'Application',
)
