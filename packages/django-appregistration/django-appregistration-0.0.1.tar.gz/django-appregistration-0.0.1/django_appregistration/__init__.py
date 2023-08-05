import threading
from pydoc import locate

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.encoding import force_text

__author__ = 'Tim Schneider <tim.schneider@northbridge-development.de>'
__copyright__ = "Copyright 2016, Northbridge Development Konrad & Schneider GbR"
__credits__ = ["Tim Schneider", ]
__maintainer__ = "Tim Schneider"
__email__ = "mail@northbridge-development.de"
__status__ = "Development"


class MultiTypePartRegistry(object):
    types = {}
    loaded = False
    lock = threading.Lock()
    part_class = None
    ignore_django_namespace = True
    call_function_subpath = None

    @classmethod
    def reset(cls):
        cls.types = {}
        cls.loaded = False

    @classmethod
    def _checked_apps(cls):
        if cls.ignore_django_namespace:
            # skip any django apps
            return [app for app in settings.INSTALLED_APPS if not app.startswith('django.')]
        return settings.INSTALLED_APPS

    @classmethod
    def add_item(cls, type, part):
        if isinstance(part, cls.part_class):
            if not type in cls.types:
                cls.types[type] = []
            cls.types[type].append(part)
        else:
            raise ValueError('Part %s is not of type %s' % (force_text(part), force_text(cls.part_class)))

    @classmethod
    def load(cls):
        with cls.lock:
            if cls.loaded == True:
                return
            if cls.part_class is None:
                raise ImproperlyConfigured('Please specify a base class for the parts that are to be loaded')

            if cls.call_function_subpath is None:
                raise ImproperlyConfigured('Please specify a python sub path for the function that is to be called')

            for app in cls._checked_apps():
                module = '%s.%s' % (app, cls.call_function_subpath)
                f = locate(module)
                if callable(f):
                    f(cls)
            cls.loaded = True

    @classmethod
    def get(cls, type):
        cls.load()
        parts = cls.types.get(type, [])
        return cls.sort_parts(parts)

    @classmethod
    def sort_parts(self, parts):
        return parts


class SingleTypePartRegistry(MultiTypePartRegistry):
    @classmethod
    def add_item(cls, part):
        return super(SingleTypePartRegistry, cls).add_item('', part)

    @classmethod
    def get(cls):
        return super(SingleTypePartRegistry, cls).get('')