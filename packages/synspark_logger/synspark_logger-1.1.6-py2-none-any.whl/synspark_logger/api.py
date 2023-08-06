import hashlib
import json
import os
import threading
import requests
import time
from .output import log


key = ''
url = 'https://api.synspark.com/v1.0/events/log'
max_retry = 10
retry_dir_path = ''


def start():
    if not retry_dir_path:
        log.critical('Retry dir path not found!')
        raise ValueError('Retry dir path not found!')

    if not os.path.exists(retry_dir_path):
        os.makedirs(retry_dir_path)

    sleep = 0
    count = 0
    for key in os.listdir(retry_dir_path):
        run_retry(key, sleep)
        count += 1
        sleep = int(count / 10)


def register_retry(data):
    global _retry

    h = hashlib.md5()
    h.update(str(data))
    key = '%s_%s' % (time.time(), h.hexdigest())
    path = os.path.join(retry_dir_path, key)

    with open(path, 'w+') as f:
        json.dump({'data': data, 'retry': 1}, f)

    run_retry(key)


def run_retry(key, sleep=0):
    threading.Thread(None, _run_retry, 'retry', (key, sleep)).start()


def send(_is_retry=False, **data):
    try:
        result = requests.post(url, data, headers={'token': key})
    except Exception as e:
        try:
            log.error('On API: %s' %  e)
            if not _is_retry:
                register_retry(data)
            return False
        except:
            raise e

    log.debug('%s %s %s' % (result.status_code, result.content, data))

    # unrecoverable error
    if 400 <= result.status_code < 500 or result.status_code == 501:
        log.error('%s statuts code(%s), data: %s' % (
            result.status_code, result.content, data
        ))
        return False

    elif result.status_code >= 500 and not _is_retry:
        log.error('%s add rety(%s), data: %s' % (
            result.status_code, result.content, data
        ))
        register_retry(data)
        return False

    return True


def _run_retry(key, sleep):
    if sleep > 0:
        time.sleep(sleep)

    path = os.path.join(retry_dir_path, key)

    with open(path, 'r') as f:
        infos = json.load(f)

    while True:
        if infos['retry'] > max_retry:
            os.remove(path)
            log.error('API max retry for: %s' % infos['data'])
            return True

        log.debug('retry for: %s' % infos['data'])
        if send(_is_retry=True, **infos['data']):
            os.remove(path)
            return True

        infos['retry'] += 1
        with open(path, 'w+') as f:
            json.dump(infos, f)
        time.sleep(infos['retry'] * 60)
