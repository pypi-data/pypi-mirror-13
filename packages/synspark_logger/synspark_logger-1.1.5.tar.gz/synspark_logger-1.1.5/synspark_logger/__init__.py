from . import api
from .backend import ALL as ALL_BACKEND
from .output import log

__version__ = '1.1.5'
NAME = 'Synspark logger'
backend = ALL_BACKEND  # default value


# public functions
def init():
    """Init Synspark logger."""
    log.info('Init %s...' % NAME)
    _call_backend('init')


def start():
    """Start Synspark logger."""
    log.info('Start %s...' % NAME)
    _call_backend('start')
    api.start()

def stop():
    """Stop Synspark logger."""
    log.info('Stop %s...' % NAME)
    _call_backend('stop')


# private functions
def _call_backend(function_name, *args, **kwargs):
    """Call all function in all backend

    :param function_name: function name
    :param args: function args
    :param kwargs: function kwargs
    """
    for name in list(backend):
        function = getattr(backend[name], function_name, None)
        if function:
            function(*args, **kwargs)