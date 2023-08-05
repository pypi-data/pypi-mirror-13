#!/usr/bin/env python
# coding: utf-8
import os
import re
import sys

from distutils.core import setup
from distutils.extension import Extension

from distutils import sysconfig

USE_CYTHON = False
if 'sdist' in sys.argv:
    USE_CYTHON = True

extensions = []
for d, s, files in os.walk("django_speedboost"):
    for fname in files:
        if fname.endswith(".c"):
            basename = fname[:-2]
            extensions.append(Extension(os.path.join(d, basename), [os.path.join(d, fname)]))

if USE_CYTHON:
    from Cython.Build import cythonize
    from Cython.Compiler.Options import directive_defaults

    directive_defaults['linetrace'] = True
    directive_defaults['binding'] = True
    extensions = cythonize("django_speedboost/*.py*")


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)

version = get_version('django_speedboost')


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read().replace('.. :changelog:', '')

site_packages_path = sysconfig.get_python_lib(plat_specific=True)
site_packages_rel_path = site_packages_path[len(sysconfig.EXEC_PREFIX) + 1:]

setup(
    name="django_speedboost",
    author="Alex Damian",
    author_email="alex@yplanapp.com",
    version=version,
    license="MIT",
    url="https://github.com/YPlan/django-speedboost",
    description="Replaces select Django modules with Cython-compiled versions for great speed.",
    long_description=readme + '\n\n' + history,
    packages=["django_speedboost"],
    ext_modules=extensions,
    install_requires=['django==1.8.8'],
    data_files=[(site_packages_rel_path, ["django_speedboost.pth"])],
    scripts="",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
)
