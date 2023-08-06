import json
import threading
from datetime import datetime, timedelta
from systemd import journal

from synspark_logger import api
from synspark_logger.output import log

# module vars
__filters = []
__journal = None
__running = False


# public functions
def add_filter(filter):
    """Add filter (rule to allow to send to api)

    :param filter: filter object
    """
    global __filters
    __filters.append(filter)

def init():
    """Init log file watcher."""
    global __journal
    __journal = journal.Reader(converters={'__CURSOR': lambda x: x})
    log.debug('Systemd initialized.')


def start():
    """Start log file watcher."""
    # Seek to now - findtime in journal
    global __running
    __journal.seek_realtime(datetime.now())

    # Move back one entry to ensure do not end up in dead space
    # if start time beyond end of journal
    try:
        __journal.get_previous()
    except OSError:
        pass  # Reading failure, so safe to ignore

    threading.Thread(None, __run, 'backend_systemd').start()
    log.debug('Systemd started.')


def stop():
    """Stop log file watcher."""
    global __journal, __running
    __journal = None
    __running = False
    log.debug('Systemd stopped.')


# private function
class JsonCast(json.JSONEncoder):
    """cast value (json serialize)"""
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

        if isinstance(o, timedelta):
            return o.total_seconds()

        return str(o)


def __run():
    """Running function"""
    global __running
    __running = True
    while __running:
        try:
            log_entry = __journal.get_next()
        except OSError:
            log.warning('Systemd: error on reading line from journal')
            continue

        # wait event (timeout on 1s for check if thread running)
        if not log_entry:
            __journal.wait(1)
            continue

        # is allowned to send to api ?
        allowed = False
        for filter in __filters:
            if filter.check(
                message=log_entry['MESSAGE'],
                criticity=log_entry['PRIORITY'],
                syslog_facility=log_entry['SYSLOG_FACILITY'],
            ):
                allowed = True
                break

        else:  # no filter => all is allowed
            allowed = True

        if allowed:
            api.send(log=json.dumps(log_entry, cls=JsonCast))
