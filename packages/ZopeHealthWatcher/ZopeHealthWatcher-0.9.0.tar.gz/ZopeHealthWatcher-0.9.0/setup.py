# -*- coding: utf8 -*-
import os
import sys
from setuptools import setup, find_packages

README = os.path.join(
    os.path.dirname(__file__),
    'README.rst'
)

install_requires = [
    'setuptools',
    'Mako'
]

if sys.version_info < (2, 5):
    install_requires.append('threadframe')

setup(
    name='ZopeHealthWatcher',
    version='0.9.0',
    description=(
        'ZopeHealthWatcher allows you to monitor and debug '
        'the threads of a Zope application.'
    ),
    long_description=open(README).read(),
    keywords='Plone Zope monitoring',
    author='Tarek Ziade',
    author_email='tarek@ziade.org',
    url='https://github.com/collective/Products.ZopeHealthWatcher',
    packages=find_packages(),
    namespace_packages=['Products'],
    install_requires=install_requires,
    license='GPL',
    zip_safe=False,
    classifiers=[
        'Framework :: Plone',
        'Framework :: Zope2',
        'Framework :: Plone :: 3.3',
        'Framework :: Plone :: 4.0',
        'Framework :: Plone :: 4.1',
        'Framework :: Plone :: 4.2',
        'Framework :: Plone :: 4.3',
        'Framework :: Plone :: 5.0',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.4',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Monitoring',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
    ],
    tests_require=['Nose'],
    test_suite='nose.collector',
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "zope_health_watcher = Products.ZopeHealthWatcher.check_zope:main",
        ]
    }
)
