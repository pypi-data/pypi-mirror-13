import asyncio
import logging
from time import time, clock

from aiohttp.web_exceptions import (
    HTTPException,
    HTTPError,
    HTTPMethodNotAllowed,
    _HTTPMove,
)

log = logging.getLogger(__name__)


@asyncio.coroutine
def logger(app, handler):
    log_logger = log.getChild('logger')

    time_start_route_resolve = time()
    clock_start_route_resolve = clock()

    @asyncio.coroutine
    def middleware(request):
        clock_delta_route_resolve = clock() - clock_start_route_resolve
        time_delta_route_resolve = time() - time_start_route_resolve

        _id = hex(id(request))[2:].upper()

        log_logger.debug("{id} - {r.method} {r.path_qs}"
                         "".format(id=_id, r=request))

        # log_logger.debug("{id} - headers - {r.headers!s}"
        #                  "".format(id=_id, r=request))

        log_logger.debug("{id} - route - t:{clock:f}ms c:{time:f}ms"
                         "".format(id=_id, rq=request,
                                   clock=clock_delta_route_resolve * 1000,
                                   time=time_delta_route_resolve * 1000))

        def log_response(response):
            # standart response log
            # this function need for log order
            clock_delta = clock() - clock_start
            time_delta = time() - time_start

            log_logger.info("{id} - {rq.method} {rq.path} "
                            "- {rp.status} - t:{clock:f}ms c:{time:f}ms"
                            "".format(id=_id, rq=request, rp=response,
                                      clock=clock_delta * 1000,
                                      time=time_delta * 1000))

        time_start = time()
        clock_start = clock()

        try:
            response = yield from handler(request)

        except _HTTPMove as exc:
            response = exc  # WAT???
            log_response(response)
            log_logger.debug("{id} - {rp}: {rp.location}"
                             "".format(id=_id, rp=response))

        except HTTPMethodNotAllowed as exc:
            response = exc
            log_response(response)
            methods = ','.join(response.allowed_methods)
            log_logger.error("{id} - {rp}: {rq.method} - {methods}"
                             "".format(id=_id, rq=request, rp=response,
                                       methods=methods))

        except HTTPError as exc:
            response = exc
            log_response(response)
            log_logger.error("{id} - {rp}: {rp.reason}"
                             "".format(id=_id, rp=response))

        except HTTPException as exc:
            response = exc
            log_response(response)
            log_logger.debug("{id} - {rp}: {rp.reason}"
                             "".format(id=_id, rp=response))

        else:
            log_response(response)

        return response

    return middleware
