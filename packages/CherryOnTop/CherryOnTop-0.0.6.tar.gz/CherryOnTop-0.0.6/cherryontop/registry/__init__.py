from cherryontop.registry.controller import icontrollers, register_controller
from cherryontop.registry.render import get_render_func, register_render_func
from cherryontop.registry.route import map_routes_for_controller
from cherryontop.registry.route import register_route


def map_all_routes(dispatcher):
    for cid, controller in icontrollers():
        map_routes_for_controller(cid, controller, dispatcher)


__all__ = [
    'map_all_routes',
    'register_controller', 'register_route',
    'get_render_func', 'register_render_func',
]
