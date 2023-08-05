#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

import os
import sys
import subprocess
import shutil
import traceback

try:
    from flake8.main import main as flake8_main
except ImportError:
    pass


def main():
    try:
        sys.argv.remove('--nolint')
    except ValueError:
        run_lint = True
    else:
        run_lint = False

    try:
        sys.argv.remove('--lintonly')
    except ValueError:
        run_tests = True
    else:
        run_tests = False

    try:
        sys.argv.remove('--nodjangotests')
    except ValueError:
        run_django_tests = True
    else:
        run_django_tests = False

    if run_tests:
        if run_django_tests:
            exit_on_failure(tests_django())

    if run_lint:
        exit_on_failure(run_setup_py_check())


_DIR_STACK = []
def _pushd(new_dir):
    global _DIR_STACK
    _DIR_STACK.append(os.getcwd())
    os.chdir(new_dir)

def _popd():
    global _DIR_STACK
    os.chdir(_DIR_STACK.pop())

def download_file(url, dest):
    try:
        import contextlib

        try:
            # For Python 3.0 and later
            from urllib.request import urlopen
        except ImportError:
            # Fall back to Python 2's urllib2
            from urllib2 import urlopen

        with contextlib.closing(urlopen(url)) as download_file:
            with open(dest, "w") as local_file:
                for chunk in download_file:
                    local_file.write(chunk)

    except Exception as e:
        print("could not retrieve: ", url)
        traceback.print_exc(e)
        return 1
    return 0


def tests_django():
    # Try to see if django-speedboost is actually hooking our imports
    try:
        import django.template.base
        assert 'speedboost' in django.template.base.__file__
    except Exception as e:
        print('Failed to verify django-speedboost is loaded.', e)
        traceback.print_exc(e)
        return 1

    python_version=str(sys.version_info[0])
    from django_speedboost import __django_version__
    env_path = os.environ['VIRTUAL_ENV']

    try:
        # download the django tarball for the version
        _pushd(env_path)
        os.makedirs("djangotests")
        exitcode = download_file("https://github.com/django/django/archive/{0}.tar.gz".format(__django_version__), "djangotests/django.tar.gz")
        _popd()

        if exitcode:
            return exitcode

        # unpack
        _pushd(os.path.join(env_path, "djangotests"))
        subprocess.call([
            'tar', 'xfz',
            'django.tar.gz',
        ])
        _popd()

        if exitcode:
            return exitcode

        # install dependencies
        _pushd(env_path)
        exitcode = subprocess.call([
            "pip", "install",
            "-r",
            "djangotests/django-{0}/tests/requirements/py{1}.txt".format(__django_version__, python_version)
        ])
        _popd()
        if exitcode:
            return exitcode

        # Run Django's test suite
        django_path = env_path + '/djangotests/django-' + __django_version__ + '/'
        return subprocess.call([
            sys.executable,
            django_path + 'tests/runtests.py',
            '--settings', 'test_sqlite',
            'template_tests', 'utils_tests',
        ])
    finally:
        shutil.rmtree(os.path.join(env_path, "djangotests"))


def run_setup_py_check():
    print('Running setup.py check')
    return subprocess.call([
        'python', 'setup.py', 'check',
        '-s', '--restructuredtext', '--metadata'
    ])


def exit_on_failure(ret, message=None):
    if ret:
        sys.exit(ret)


if __name__ == '__main__':
    main()
