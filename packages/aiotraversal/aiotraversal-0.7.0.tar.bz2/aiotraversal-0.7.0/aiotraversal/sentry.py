import asyncio
import logging
import sys
import warnings

from raven import Client
from raven_aiohttp import AioHttpTransport

from aiohttp.web_exceptions import HTTPRedirection, HTTPSuccessful

log = logging.getLogger(__name__)


def includeme(app):
    if ('sentry' not in app['settings'] or
            'dsn' not in app['settings']['sentry']):
        warnings.warn('sentry not configured')
        return

    app.add_method('get_sentry', get_sentry)
    app._middlewares.append(sentry)


def get_sentry(app, **context):
    """ Return client for sentry
    """
    context.setdefault('settings', app['settings'])
    context.setdefault('sys.argv', sys.argv[:])

    settings = app['settings']['sentry']

    return Client(
        dsn=settings['dsn'],
        transport=AioHttpTransport,
        include_paths=settings.get('include_paths'),
        exclude_paths=settings.get('exclude_paths'),
        tags=settings.get('tags'),
        context=context)


@asyncio.coroutine
def sentry(app, handler):
    @asyncio.coroutine
    def middleware(request):
        try:
            return (yield from handler(request))
        except (HTTPRedirection, HTTPSuccessful) as exc:
            raise exc
        except Exception as exc:
            get_sentry(app, request=request).captureException()
            raise exc

    return middleware
