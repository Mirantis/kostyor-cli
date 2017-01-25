#!/usr/bin/env python
from setuptools import setup, find_packages

PROJECT = 'kostyor-cli'

VERSION = '0.1'


try:
    long_description = open('README.rst', 'rt').read()
except IOError:
    long_description = ''

setup(
    name=PROJECT,
    version=VERSION,

    description='Kostyor CLI tool',
    long_description=long_description,

    author='Kostyor Authors',
    author_email='TODO',

    url='https://github.com/sc68cal/kostyor-cli',
    download_url='https://github.com/sc68cal/kostyor-cli/tarball/master',

    classifiers=['Development Status :: 3 - Alpha',
                 'License :: OSI Approved :: Apache Software License',
                 'Programming Language :: Python',
                 'Programming Language :: Python :: 2',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3',
                 'Programming Language :: Python :: 3.4',
                 'Intended Audience :: Developers',
                 'Environment :: Console',
                 ],

    platforms=['Any'],

    scripts=[],

    provides=[],
    install_requires=['cliff'],

    namespace_packages=[],
    packages=find_packages(),
    include_package_data=True,

    entry_points={
        'console_scripts': [
            'kostyor = kostyor_cli.main:main'
        ],
        'kostyor.cli': [
            'check-upgrade = kostyor_cli.main:CheckUpgrade',
            'cluster-status = kostyor_cli.main:ClusterStatus',
            'cluster-list = kostyor_cli.main:ClusterList',
            'list-upgrade-versions = kostyor_cli.main:ListUpgradeVersions',
            'host-list = kostyor_cli.main:HostList',
            'service-list = kostyor_cli.main:ServiceList',

            'discover-list = kostyor_cli.commands:DiscoverList',
            'discover-run = kostyor_cli.commands:DiscoverRun',

            'upgrade-list = kostyor_cli.commands:UpgradeList',
            'upgrade-show = kostyor_cli.commands:UpgradeShow',
            'upgrade-start = kostyor_cli.commands:UpgradeStart',
            'upgrade-pause = kostyor_cli.commands:UpgradePause',
            'upgrade-continue = kostyor_cli.commands:UpgradeContinue',
            'upgrade-rollback = kostyor_cli.commands:UpgradeRollback',
            'upgrade-cancel = kostyor_cli.commands:UpgradeCancel',
        ],
    },

    zip_safe=False,
)
