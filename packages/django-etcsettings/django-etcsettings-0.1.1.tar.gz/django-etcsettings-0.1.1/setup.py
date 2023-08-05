# coding: utf-8

from distutils.core import setup


VERSION = open('VERSION').read().strip()
REQUIREMENTS = [line.strip() for line in open('requirements.txt')]


setup(
    name='django-etcsettings',
    packages=['etcsettings'],
    version=VERSION,
    description='A simple settings from yaml file loader',
    author='Denis Lesnov',
    author_email='denis+etcsettings@lesnov.me',
    url='https://github.com/Leden/django-etcsettings',
    download_url='https://github.com/Leden/django-etcsettings/tarball/%s' % VERSION,
    requires=REQUIREMENTS,
    keywords=['django', 'settings', 'yaml'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Framework :: Django',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
