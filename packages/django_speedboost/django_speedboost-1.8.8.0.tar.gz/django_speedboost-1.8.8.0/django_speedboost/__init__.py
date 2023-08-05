# -*- encoding:utf-8 -*-
from __future__ import absolute_import, division, unicode_literals, print_function

import importlib
import sys

__django_version__ = '1.8.8'
__version__ = '1.8.8.0'
# Can't concat __django_version__ in __version__ because it breaks setup.py
assert __version__.startswith(__django_version__)

MODULE_NAMES = ["context", "context_processors", "base", "defaulttags"]


for module_name in MODULE_NAMES:
    assert "django.template.%s" % module_name not in sys.modules


class DjangoSpeedboostImporter(object):

    original_template_modules = ["django.template.%s" % module_name for module_name in MODULE_NAMES]
    replcmnt_template_modules = ["django_speedboost.%s" % module_name for module_name in MODULE_NAMES]
    paths = {}

    def find_module(self, full_name, path=None):
        if full_name in self.original_template_modules:
            self.paths[full_name] = path
            return self
        if full_name.startswith("django_speedboost.") and full_name not in self.replcmnt_template_modules:

            sys.meta_path.remove(self)
            try:
                importlib.import_module(full_name.replace("django_speedboost.", "django.template."))
            except ImportError:
                return None
            finally:
                sys.meta_path.append(self)

            return self
        return None

    def load_module(self, name):
        if name in sys.modules:
            return sys.modules[name]

        if name in self.original_template_modules:
            imported_module = importlib.import_module(name.replace("django.template", "django_speedboost"))
            sys.modules[name] = imported_module
            return imported_module

        if name.startswith("django_speedboost.") and name not in self.replcmnt_template_modules:
            m_name = name.replace("django_speedboost", "django.template")
            sys.meta_path.remove(self)
            imported_module = importlib.import_module(m_name)
            sys.meta_path.append(self)
            sys.modules[name] = imported_module
            return imported_module

        raise ImportError("Could not load %s" % name)

sys.meta_path.append(DjangoSpeedboostImporter())
