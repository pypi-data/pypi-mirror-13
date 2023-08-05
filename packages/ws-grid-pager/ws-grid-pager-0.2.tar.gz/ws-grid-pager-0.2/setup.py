# -*- coding: utf-8 -*-
from os.path import join, dirname

from setuptools import setup, find_packages

README = open(join(dirname(__file__), 'README.rst')).read()
setup(
    name='ws-grid-pager',
    version='0.2',
    packages=find_packages(),
    package_data={},
    entry_points={
        'console_scripts': [
            'ws-grid-pager=ws_grid_pager.ws_grid_pager:run',
            'gp-switch-workspace=ws_grid_pager.grid_pager_switch_workspace:run',
            'gp-send-window=ws_grid_pager.grid_pager_send_window:run',
            'gp-take-window=ws_grid_pager.grid_pager_take_window:run'
        ]
    },
    include_package_data=True,
    install_requires=[],
    license='GNU General Public License v2 (GPLv2)',
    description='A workspace grid pager for EMWH-compliant window-managers',
    long_description=README,
    url='https://github.com/ckot/ws-grid-pager',
    download_url='https://github.com/ckot/ws-grid-pager/archive/master.zip',
    author='Scott Silliman',
    author_email='scott.t.silliman@gmail.com',
    maintainer='Scott Silliman',
    maintainer_email='scott.t.silliman@gmail.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Desktop Environment :: Window Managers',
        'Topic :: Desktop Environment :: Window Managers :: Fluxbox',
    ],
)
