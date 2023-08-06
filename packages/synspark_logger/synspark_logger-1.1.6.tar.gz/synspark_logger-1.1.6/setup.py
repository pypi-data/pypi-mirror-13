import os
from setuptools import setup, find_packages
from glob import glob

try:
    # python 3
    from distutils.command.build_py import build_py_2to3 as build_py
    from distutils.command.build_scripts \
        import build_scripts_2to3 as build_scripts
except ImportError:
    # python 2
    from distutils.command.build_py import build_py
    from distutils.command.build_scripts import build_scripts

import synspark_logger


# get the long description from the README file
path = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(path, 'README.rst')) as f:
    long_description = f.read()


setup(
    version=synspark_logger.__version__,
    name='synspark_logger',
    packages=find_packages(),
    url='https://www.synspark.com',
    description='Collect your security events to allow you to visualize it on Synspark.',
    long_description=long_description,
    license='',
    platforms='Posix',
    author='Synspark',
    author_email='matthieu.chevrier@synhack.fr',
    data_files=[
        ('etc/synspark_logger', glob('config/*.cfg')),
        ('usr/share/doc/synspark_logger', ['README.rst']),
    ],
    cmdclass={
        'build_py': build_py,
        'build_scripts': build_scripts,
    },
    scripts=[
        'bin/synspark-logger',
    ],
    install_requires=[
        'requests',
    ],

    # see https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # how mature is this project? Common values are
        #   3 - alpha
        #   4 - beta
        #   5 - production/stable
        'Development Status :: 3 - Alpha',

        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Topic :: Internet :: Log Analysis',
        'Topic :: Security',
        'Topic :: System :: Logging',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ]
)