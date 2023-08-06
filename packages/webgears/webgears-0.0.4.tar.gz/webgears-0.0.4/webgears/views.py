"""Views module."""

import six

from werkzeug import wrappers

from dependency_injector import catalogs
from dependency_injector import providers

from webgears import routing


class Request(wrappers.Request):
    """View request."""


class Response(wrappers.Response):
    """View response."""


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
