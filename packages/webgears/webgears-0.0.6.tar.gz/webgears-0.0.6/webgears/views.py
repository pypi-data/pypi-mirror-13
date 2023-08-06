"""Views module."""

import six

from werkzeug import wrappers
from werkzeug import utils
from werkzeug import exceptions

from dependency_injector import catalogs
from dependency_injector import providers

from webgears import routing
from webgears import json


class Request(wrappers.Request):
    """View request."""


class Response(wrappers.Response):
    """View response."""


class View(object):
    """Base view."""

    def __init__(self, request, router_adapter, jinja_env):
        """Initializer."""
        self.request = request
        self.router_adapter = router_adapter
        self.jinja_env = jinja_env
        super(View, self).__init__()

    def handle_request(self, **kwargs):
        """Handle request."""
        http_method = self.request.method.lower()
        try:
            http_method_handler = getattr(self, http_method)
        except AttributeError:
            return exceptions.MethodNotAllowed()
        else:
            return http_method_handler(**kwargs)

    def render_template(self, template_path, context=None):
        """Render template with specified context."""
        if not context:
            context = dict()
        context.update({
            'request': self.request,
            'url_for': self.url_for,
        })
        template = self.jinja_env.get_template(template_path)
        return template.render(context).encode('utf-8')

    def url_for(self, endpoint, values=None, method=None, force_external=False,
                append_unknown=True):
        """Build an url for specified endpoint."""
        return self.router_adapter.build(endpoint, values, method,
                                         force_external, append_unknown)

    def redirect(self, *args, **kwargs):
        """Create and return redirect response."""
        return utils.redirect(*args, **kwargs)

    def html(self, template_path, context=None):
        """Render template with context and return result as html response."""
        return Response(self.render_template(template_path, context),
                        mimetype='text/html')

    def json(self, context=None):
        """Dump context to the json and return result as json response."""
        return Response(json.dumps(context), mimetype='application/json')


class Provider(providers.Factory):
    """View provider."""

    provided_type = View


class CatalogMetaClass(catalogs.DeclarativeCatalogMetaClass):
    """View providers catalog metaclass."""

    def __new__(mcs, class_name, bases, attributes):
        """Declarative catalog meta class."""
        cls = catalogs.DeclarativeCatalogMetaClass.__new__(mcs,
                                                           class_name,
                                                           bases,
                                                           attributes)
        cls.RulesMap = type('RulesMap',
                            tuple([routing.RulesMap]),
                            {'views_catalog': cls})
        return cls


@six.add_metaclass(CatalogMetaClass)
class Catalog(catalogs.DeclarativeCatalog):
    """View providers catalog."""

    provider_type = Provider


__all__ = (
    'Catalog',
    'Provider',
    'View',
)
