import imp
import os
from subprocess import check_output

from synspark_logger.output import log


files_path = {
    # name: path
    'systemctl': {
        'path': '/lib/systemd/system/synspark_logger.service',
        'post_install_cmd': 'systemctl daemon-reload && '
                            'systemctl start synspark_logger && '
                            'systemctl enable synspark_logger',
        'post_uninstall_cmd': 'systemctl daemon-reload',
        'pre_uninstall_cmd': 'systemctl disable synspark_logger && '
                             'systemctl is-active synspark_logger && '
                             'systemctl stop synspark_logger',
    },
}


def install_daemon():
    log.info('install daemon ...')
    bin_path = check_output(['whereis', 'synspark-logger']).split()[-1].strip()

    template_data = {
        'bin_path': bin_path,
    }

    print(template_data)

    for name, data in files_path.items():
        path = data['path']

        if os.path.exists(path):
            log.warning('%s: "%s" already exist.' % (name, path))
            continue

        _run_command(name, data, 'pre_install_cmd')

        file_name = path.split('/')[-1]
        current_dir_path = os.path.dirname(os.path.abspath(__file__))
        source_path = os.path.join(current_dir_path, 'files', file_name + '.py')

        # for import file with dot
        with open(source_path, 'rb') as f:
            template = imp.load_module('content', f, file_name + '.py',
                ('.py', 'rb', imp.PY_SOURCE)
            ).template

        with open(path, 'w') as f:
            f.write(template % template_data)
            log.info('%s: "%s" created.' % (name, path))

        _run_command(name, data, 'post_install_cmd')

    log.info('install done ...')


def uninstall_daemon():
    log.info('uninstall daemon ...')

    for name, data in files_path.items():
        path = data['path']

        if os.path.exists(path):
            _run_command(name, data, 'pre_uninstall_cmd')

            os.remove(path)
            log.info('%s: "%s" removed.' % (name, path))

        _run_command(name, data, 'post_uninstall_cmd')

    log.info('uninstall done ...')


def _run_command(name, data, cmd_index):
    cmd = data.get(cmd_index)

    if cmd:
        cmd_text = cmd_index.replace('_', ' ')
        log.debug('%s: command: "%s"' % (name, cmd))
        log.info('%s: run %s.' % (name, cmd_text))

        code = os.system(cmd)
        if code != 0:
            log.error('%s: fail %s (code: %d).' % (name, cmd_text, code))