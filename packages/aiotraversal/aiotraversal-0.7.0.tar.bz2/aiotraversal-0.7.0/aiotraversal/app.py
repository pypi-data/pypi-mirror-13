import asyncio
from types import MethodType
import warnings
import logging

from aiohttp.web import Application as BaseApplication
from aiohttp_traversal import TraversalRouter
from aiohttp_traversal.ext.resources import add_child
from aiohttp_exc_handlers import exc_handlers_middleware, bind_exc_handler

import includer
from resolver_deco import resolver


log = logging.getLogger(__name__)


class _AiotraversalIncluderMixin(includer.IncluderMixin):
    def _includer_get_wrapper(self, include_module):
        return _AiotraversalIncluderWrapper(self, include_module)

    @property
    def __package_for_resolve_deco__(self):
        return self._include_module


class _AiotraversalIncluderWrapper(_AiotraversalIncluderMixin,
                                   includer._IncluderWrapper):
    pass


class Application(_AiotraversalIncluderMixin, BaseApplication):
    """ Main application object
    """
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('router', TraversalRouter())
        kwargs.setdefault('middlewares', [exc_handlers_middleware])
        super().__init__(*args, **kwargs)

        self.router.set_root_factory('aiohttp_traversal.ext.resources.Root')

        self._middlewares = list(self._middlewares)  # some monkey patching

        self.add_method('add_child', add_child)

        self['settings'] = {}

        self['settings'].setdefault('host', 'localhost')
        self['settings'].setdefault('port', 8080)

    def start(self, loop):
        """ Start applisation and add to event loop
        """
        self._middlewares = tuple(self._middlewares)

        host = self['settings']['host']
        port = self['settings']['port']

        f = loop.create_server(self.make_handler(), host, port)
        srv = loop.run_until_complete(f)
        log.info("listening - {}:{}".format(host, port))
        return srv

    @resolver('func')
    def add_method(self, name, func):
        """ Add method to application

        Usage from configuration process.
        """
        if not isinstance(name, str):
            raise TypeError("name is not a string!")

        if hasattr(self, '_app'):
            app = self._app
        else:
            app = self

        if hasattr(app, name):
            warnings.warn("Method {} is already exist, replacing it"
                          "".format(name))

        meth = MethodType(func, app)
        setattr(app, name, meth)

    @resolver('resource', 'view')
    def bind_view(self, resource, view, tail=()):
        """ Bind view to resource
        """
        log.debug("bind_view({!r}, {!r}, {!r}, {!r})"
                  "".format(self, resource, view, tail))

        if issubclass(resource, Exception):
            if tail:
                raise TypeError("tail not accepted for exception resources")

            bind_exc_handler(self, resource, view)
        else:
            self.router.bind_view(resource, view, tail)

    def get_root(self, *args, **kwargs):
        """ Return new root of resource tree
        """
        return self.router.get_root(self, *args, **kwargs)
