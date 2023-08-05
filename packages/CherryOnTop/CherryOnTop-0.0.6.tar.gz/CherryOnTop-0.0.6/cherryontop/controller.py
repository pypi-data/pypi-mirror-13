import functools
import uuid

import ujson

from cherryontop.errors import error_response_handler
from cherryontop.registry import get_render_func
from cherryontop.registry import register_controller, register_route


def _render(f):
    @functools.wraps(f)
    def wrap(*a, **kw):
        render_func = get_render_func()
        closure = lambda: f(*a, **kw)
        return render_func(closure) if render_func else closure()
    return wrap


def _to_json(f):
    @functools.wraps(f)
    def wrap(*a, **kw):
        data = f(*a, **kw)
        return ujson.dumps(data)
    return wrap


class _Base(type):
    def __new__(cls, name, bases, dct):
        if len(bases) == 1 and bases[0] == object:  # is base Controller?
            return super(_Base, cls).__new__(cls, name, bases, dct)

        cid = uuid.uuid4().hex

        for key, val in dct.items():
            if hasattr(val, '_cbs_routes'):  # is a handler
                for route, method in val._cbs_routes:
                    register_route(cid,
                                   route,
                                   val.__name__,
                                   conditions={'method': [method]})

                f = _render(val)
                f = _to_json(f)
                dct[key] = f

        the_class = super(_Base, cls).__new__(cls, name, bases, dct)

        cp_config = getattr(the_class, '_cp_config', {})
        if 'request.error_response' not in cp_config:
            cp_config['request.error_response'] = error_response_handler
            setattr(the_class, '_cp_config', cp_config)

        register_controller(cid, the_class)

        return the_class


class Controller(object):

    __metaclass__ = _Base
