"""Views module."""

import six

from dependency_injector import catalogs
from dependency_injector import providers

from werkzeug import wrappers


class Route(object):
    """Route."""

    def __init__(self, pattern, view_provider=None, redirect_to=None):
        """Initializer."""
        self.pattern = pattern
        self.view_provider = view_provider
        self.redirect_to = redirect_to
        self.views_catalog = None
        super(Route, self).__init__()

    @property
    def endpoint(self):
        """Endpoint name."""
        if not self.view_provider:
            return None
        return '.'.join((
            self.views_catalog.__name__,
            self.views_catalog.get_provider_bind_name(self.view_provider)
        ))


class RoutesMap(object):
    """View providers catalog routes map."""

    views_catalog = None

    def __init__(self, routes, prefix=None):
        """Initializer."""
        self.routes = routes
        for route in self.routes:
            route.views_catalog = self.__class__.views_catalog
            if prefix:
                route.pattern = ''.join((prefix, route.pattern))
        super(RoutesMap, self).__init__()


class View(object):
    """Base view."""

    def __init__(self, request):
        """Initializer."""
        self.request = request
        super(View, self).__init__()


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
        cls.RoutesMap = type('RoutesMap', (RoutesMap,), {'views_catalog': cls})
        return cls


@six.add_metaclass(CatalogMetaClass)
class Catalog(catalogs.DeclarativeCatalog):
    """View providers catalog."""

    provider_type = Provider


Response = wrappers.Response
