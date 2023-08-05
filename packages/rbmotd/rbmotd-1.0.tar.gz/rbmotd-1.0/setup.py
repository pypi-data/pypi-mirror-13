#!/usr/bin/env python

from reviewboard.extensions.packaging import setup

from rbmotd import get_package_version


PACKAGE = 'rbmotd'

setup(
    name=PACKAGE,
    version=get_package_version(),
    description='Message of the Day support for Review Board',
    url='https://www.reviewboard.org/',
    author='Beanbag, Inc.',
    author_email='support@beanbaginc.com',
    maintainer='Beanbag, Inc.',
    maintainer_email='support@beanbaginc.com',
    packages=['rbmotd'],
    entry_points={
        'reviewboard.extensions': [
            'rbmotd = rbmotd.extension:MotdExtension',
        ],
    },
    package_data={
        'rbmotd': [
            'templates/rbmotd/*.html',
        ]
    },
)
