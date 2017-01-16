# -*- coding: utf-8 -*-
# FileName      : 'setup.py'
# CreateTime    : '2017/1/10 18:13'
# CreateAuthor  : 'Mundy'

import os
import sys
import re
from distutils.sysconfig import get_python_lib

from setuptools import find_packages, setup

overlay_warning = False
if "install" in sys.argv:
    lib_paths = [get_python_lib()]
    if lib_paths[0].startswith("/usr/lib/"):
        # We have to try also with an explicit prefix of /usr/local in order to
        # catch Debian's custom user site-packages directory.
        lib_paths.append(get_python_lib(prefix="/usr/local"))
    for lib_path in lib_paths:
        existing_path = os.path.abspath(os.path.join(lib_path, "djangoautocreate"))
        if os.path.exists(existing_path):
            # We note the need for the warning here, but present it after the
            # command is run, so it's more likely to be seen.
            overlay_warning = True
            break


try:
    from pypandoc import convert

    def read_md(f):
        return convert(f, 'rst')
except ImportError:
    print("warning: pypandoc module not found, could not convert Markdown to RST")

    def read_md(f):
        return open(f, 'r').read()


def get_packages(package):
    """
    Return root package and all sub-packages.
    """
    return [dirpath for dirpath, dirnames, filenames in os.walk(package)]


def get_package_data(package):
    """
    Return all files under the root package, that are not in a
    package themselves.
    """
    walk = [(dirpath.replace(package + os.sep, '', 1), filenames)
            for dirpath, dirnames, filenames in os.walk(package)
            if not os.path.exists(os.path.join(dirpath, '__init__.py'))]
    filepaths = []
    for base, filenames in walk:
        filepaths.extend([os.path.join(base, filename)
                          for filename in filenames])
    return {package: filepaths}


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)


EXCLUDE_FROM_PACKAGES = []

setup(
    name='django-auto-create',
    version=get_version('django_auto'),
    url='http://blog.scmud.com',
    description='Automatically create a django project and the environment, start the app, automatic configuration '
                'Settings. The py, provide common orders to each type',
    long_description=read_md('README.md'),
    author='Mundy',
    author_email='mudong1991@163.com',
    license=open('LICENSE').read(),
    download_url='http://github.com/mudong1991/django-auto-create/archive/master.zip',
    packages=find_packages(exclude=EXCLUDE_FROM_PACKAGES),
    package_data=get_package_data('django_auto'),
    include_package_data=True,
    scripts=['django_auto/bin/django-auto-admin.py'],
    entry_points={'console_scripts': [
        'django-auto-admin = django_auto.core.management:execute_from_command_line',
    ]},
    install_requires=[
        'pip',
        'django>=1.10',
        'virtualenv>=1.11'
    ],
    extras_require={
        'Reversion': ['django-reversion'],
    },
    zip_safe=False,
    keywords=['django auto', 'django', 'django create'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        "Programming Language :: Python :: 2.7",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ]
)

if overlay_warning:
    sys.stderr.write("""

========
WARNING!
========

You have just installed Django over top of an existing
installation, without removing it first. Because of this,
your install may now include extraneous files from a
previous version that have since been removed from
Django. This is known to cause a variety of problems. You
should manually remove the

%(existing_path)s

directory and re-install Django.

""" % {"existing_path": existing_path})