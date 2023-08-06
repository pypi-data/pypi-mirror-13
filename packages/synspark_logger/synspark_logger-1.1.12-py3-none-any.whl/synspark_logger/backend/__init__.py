from synspark_logger.output import log

ALL = {}

try:
    from . import files
    ALL['files'] = files
except ImportError as e:
    log.warning('Disable backend (files): %s' % e)

try:
    from . import systemctl
    ALL['systemctl'] = systemctl
except ImportError as e:
    log.warning('Disable backend (systemctl): %s' % e)
