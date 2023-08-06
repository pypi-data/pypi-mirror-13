Collect your security events to allow you to visualize it on Synspark.

************
Installation
************

Required package:

- `[Python2 >= 2.7 or Python >= 3.2] <http://www.python.org>`_
- `[requests] <python-requests.org>`_

Optional packages:

- `[pyinotify] <https://github.com/seb-m/pyinotify>`_
- `[systemd] <http://www.freedesktop.org/wiki/Software/systemd>`_

Edit your config file located at (set your api key):

- on python virtualenv: <VIRTUALENV_PATH>etc/synspark_logger/synspark_logger.cfg
- on system: /usr/local/etc/synspark_logger/synspark_logger.cfg

Enable system deamon:

.. code:: shell

  sudo synspark-logger install_daemon
