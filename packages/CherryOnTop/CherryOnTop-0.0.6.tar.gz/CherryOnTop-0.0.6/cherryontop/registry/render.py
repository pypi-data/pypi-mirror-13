_render_func = None


def register_render_func(f):
    if not callable(f):
        raise TypeError('render_func not callable')

    global _render_func
    _render_func = f


def get_render_func():
    return _render_func
