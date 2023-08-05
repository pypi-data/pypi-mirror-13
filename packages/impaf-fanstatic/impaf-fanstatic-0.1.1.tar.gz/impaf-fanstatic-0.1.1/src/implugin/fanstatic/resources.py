from importlib import import_module

from fanstatic import Resource


class NameNotKnowError(Exception):

    def __init__(self, name):
        self.name = name


class ModuleNotFound(Exception):

    def __init__(self, module):
        self.module = module


class Resources(object):

    _statics_default = {
        'jquery': 'js.jquery:jquery',
        'bootstrap': 'js.bootstrap:bootstrap',
    }

    def __init__(self):
        self.statics = dict(self._statics_default)

    def add_resource(self, name, lib):
        self.statics[name] = lib

    def need(self, lib):
        self._get_lib(lib).need()
        return ''

    def _get_lib(self, name):
        lib = self._get_url(name)
        if self._is_resource(lib):
            return lib
        else:
            return self._import_lib(lib)

    def _get_url(self, name):
        try:
            return self.statics[name]
        except KeyError:
            raise NameNotKnowError(name)

    def _is_resource(self, lib):
        return isinstance(lib, Resource)

    def _import_lib(self, url):
        module_url, attrname = url.split(':')
        try:
            module = import_module(module_url)
        except ImportError:
            raise ModuleNotFound(module_url)

        try:
            return getattr(module, attrname)
        except AttributeError:
            raise ModuleNotFound(url)
