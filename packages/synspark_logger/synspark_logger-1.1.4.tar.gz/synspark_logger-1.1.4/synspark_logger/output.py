import logging
import sys


# Gets the instance of the logger.
log = logging.getLogger('Synspark_logger')


# Init output log: redirect log to cli and edit format
if not(len(log.handlers)):
    logout = logging.StreamHandler(sys.stdout)
    logout.setFormatter(logging.Formatter('%(levelname)-6s %(message)s'))
    log.addHandler(logout)