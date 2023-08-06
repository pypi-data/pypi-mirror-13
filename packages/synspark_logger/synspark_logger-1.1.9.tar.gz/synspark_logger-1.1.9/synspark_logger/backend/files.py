import os
import pyinotify

from synspark_logger import api
from synspark_logger.output import log

# module vars
__monitor = None
__notifier = None
__watcher = {}


# public functions
def init():
    """Init log file watcher."""
    global __monitor
    __monitor = pyinotify.WatchManager()
    log.debug('Pyinotify initialized.')


def start():
    """Start log file watcher."""
    global __notifier
    __notifier = pyinotify.ThreadedNotifier(__monitor, ProcessPyinotify())
    __notifier.start()
    log.debug('Pyinotify started.')


def stop():
    """Stop log file watcher."""
    global __notifier, __monitor
    __notifier.stop()  # Stop the notifier thread
    __notifier.join()  # wait done
    __notifier = None
    __monitor = None
    log.debug('Pyinotify stopped.')


def watcher_add(path, read_all=False, filter={}):
    """Add path from watcher.

    :param path:  log path
    :param read_all: on file created: start read to begin
    :param filter: filters rules object
    """
    # clean value
    path = path.strip()
    if not path or path in __watcher:
        return

    # parent directory (log rotate,, create, ...)
    if os.path.isdir(path):
        mask = pyinotify.IN_CREATE | pyinotify.IN_MOVED_TO
        __watcher[path] = {
            'watch': __monitor.add_watch(path, mask),
        }

    # file
    else:
        watcher_add(os.path.dirname(path))  # add parent directory

        if os.path.isfile(path):
            seek = 0 if read_all else os.stat(path).st_size
            mask = pyinotify.IN_MODIFY | pyinotify.IN_DELETE_SELF
            watch = __monitor.add_watch(path, mask).values()[0]

        else:  # file not exist for the moment
            seek = 0
            watch = None

        __watcher[path] = {
            'seek': seek,
            'watch': watch,
            'filter': filter,
        }
    log.debug('Pyinotify: Watcher add %s' % path)


def watcher_del(path):
    """Remove path from watcher.

    :param path:  log path
    :return: is cleaned remove
    """
    if path not in __watcher:
        return False

    result = True

    if __watcher[path]['watch']:
        result &= __monitor.rm_watch(__watcher[path]['watch']).values()[0]

    del(__watcher[path])
    log.debug('Pyinotify: Watcher del %s', path)
    return result


# private functions
class ProcessPyinotify(pyinotify.ProcessEvent):
    """Pyinotify event handler."""
    def process_default(self, event):
        try:
            _callback(event)
        except Exception as e:
            log.error('Error in ProcessPyinotify: %s' % e, exc_info=True)


def _callback(event):
    """Calback for process Pyinotify event.

    :param event: Pyinotify event
    """
    log.debug('Pyinotify: callback for %s', event)
    path = event.pathname

    if event.mask & pyinotify.IN_ISDIR:
        log.debug('Pyinotify: Ignoring directory event at %s' % path)
        return

    # create or moved: log rotate, new process, ...
    if event.mask & (pyinotify.IN_CREATE | pyinotify.IN_MOVED_TO |
                     pyinotify.IN_DELETE_SELF):
        if path not in __watcher:
            log.debug('Pyinotify: Ignoring of %s we do not monitor' % path)
            return

        # refresh watcher
        watcher_del(path)
        watcher_add(path, read_all=True)  # file created: start read to begin

    # read new log lines
    _read_new_line(path)


def _read_new_line(path):
    """Read new log file and send to api.

    :param path: log path
    """
    if not os.path.isfile(path):  # don't read on deleted events
        return

    with open(path, 'r') as f:
        f.seek(__watcher[path]['seek'])  # set position at last read
        filter = __watcher[path]['filter']

        # get new lines
        for line in f.readlines():
            line = line.strip()

            if filter.check(message=line):
                api.send(log=line, path=path)

    # save new position
    __watcher[path]['seek'] = os.stat(path).st_size
