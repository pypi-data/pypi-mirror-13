#!/usr/bin/env python

from setuptools import setup
from setuptools.command.install import install as _install

class install(_install):
    def pre_install_script(self):
        pass

    def post_install_script(self):
        pass

    def run(self):
        self.pre_install_script()

        _install.run(self)

        self.post_install_script()

if __name__ == '__main__':
    setup(
        name = 'succubus',
        version = '1.0-9',
        description = '''Lightweight Python module for daemonizing''',
        long_description = '''========
succubus
========

Description
===========
succubus is a lightweight python module for a fast and easy creation of
python daemons.

Examples
========

.. code-block:: python

    import logging
    import sys

    from logging.handlers import WatchedFileHandler

    from succubus import Daemon


    class MyDaemon(Daemon):
        def __init__(self, *args, **kwargs):
            super(MyDaemon, self).__init__(*args, **kwargs)

        def run(self):
            """Overwrite the run function of the daemon class"""
            handler = WatchedFileHandler('succubus.log')
            self.logger = logging.getLogger('succubus')
            self.logger.addHandler(handler)
            while True:
                time.sleep(1)
                self.logger.warn('Hello world')


    def main():
        daemon = MyDaemon(pid_file='succubus.pid')
        sys.exit(daemon.action())


    if __name__ == '__main__':
        main()
''',
        author = "Stefan Neben, Stefan Nordhausen",
        author_email = "stefan.neben@immobilienscout24.de, stefan.nordhausen@immobilienscout24.de",
        license = 'Apache License 2.0',
        url = 'https://github.com/ImmobilienScout24/succubus',
        scripts = [],
        packages = ['succubus'],
        py_modules = [],
        classifiers = [
            'Development Status :: 3 - Alpha',
            'Programming Language :: Python'
        ],
        entry_points = {},
        data_files = [],
        package_data = {},
        install_requires = [],
        dependency_links = [],
        zip_safe=True,
        cmdclass={'install': install},
    )
