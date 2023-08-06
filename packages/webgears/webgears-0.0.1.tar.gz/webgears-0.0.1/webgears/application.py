"""Application module."""

from werkzeug import routing
from werkzeug import wrappers
from werkzeug import exceptions


class Application(object):
    """Base application."""

    route_maps = []

    def __init__(self):
        """Initializer."""
        routing_rules = []
        for routes_map in self.__class__.route_maps:
            for route in routes_map.routes:
                rule = routing.Rule(route.pattern,
                                    endpoint=route.endpoint,
                                    redirect_to=route.redirect_to)
                rule.view_provider = route.view_provider
                routing_rules.append(rule)
        self.router = routing.Map(routing_rules)

    def __call__(self, environ, start_response):
        """Wsgi application callback."""
        request = wrappers.Request(environ)

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
            return exception
        else:
            return response(environ, start_response)


__all__ = (
    'Application',
)
