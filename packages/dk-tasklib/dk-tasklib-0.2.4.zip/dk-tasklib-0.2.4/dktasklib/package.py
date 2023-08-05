# -*- coding: utf-8 -*-

import json
import os

from ConfigParser import RawConfigParser, NoOptionError
from dkfileutils.pfind import pfind


class PackageInterface(object):

    def upversion(self, major=False, minor=False, patch=False):
        """Update package version (default patch-level increase).
        """
        if not (major or minor or patch):
            # this is normally set by version.upversion
            patch = True  # pragma: nocover
        version = [int(n, 10) for n in self.version.split('.')]
        if major:
            version[0] += 1
        if minor:
            version[1] += 1
        if patch:
            version[2] += 1
        newversion = '.'.join([str(n) for n in version])
        self['version'] = newversion
        return newversion

    # for convenience (continue using [](__setitem__) for setting).
    def __getattr__(self, item):
        return self[item]

    def __setitem__(self, key, value):  # pragma: nocover
        # should override
        pass

    def __getitem__(self, item, default=None):  # pragma: nocover
        # should override
        return ''

    def get(self, key, default=None):
        return self.__getitem__(key, default)


class PackageIni(PackageInterface):
    """Read package.ini or dkbuild.ini file::

           pkg = dktasklib.Package()
           VERSION = pkg.version

    """
    @classmethod
    def exists(cls):
        return pfind('.', 'package.ini') or pfind('.', 'dkbuild.ini')

    def __init__(self, *args, **kw):
        self.fname = pfind('.', 'package.ini') or pfind('.', 'dkbuild.ini')
        if self.fname is None:  # pragma: nocover
            raise RuntimeError("""
                I couldn't find a package.json, package.ini,
                or dkbuild.ini file starting from %s.
                """ % os.getcwd())
        self.root = os.path.dirname(self.fname)
        self._package = None

    def _open(self, fname):
        self._package = RawConfigParser()
        self._package.read(self.fname)

    @property
    def package(self):
        if not self._package:
            self._open(self.fname)
        return self._package

    def __setitem__(self, attr, val):
        self.package.set('package', attr, val)
        self.package.write(open(self.fname, 'w'))

    def __getitem__(self, attr, default=None):
        try:
            return self.package.get('package', attr)
        except (KeyError, NoOptionError):
            # return default
            if default is not None:
                return default
            raise AttributeError(
                self.fname + " does not have an attribute named: " + attr)


class PackageJson(PackageInterface):
    """Read package.json file::

           pkg = dktasklib.Package()
           VERSION = pkg.version

    """
    @classmethod
    def exists(cls):
        return pfind('.', 'package.json')

    def __init__(self, basedir=None, packagejson='package.json'):
        if basedir is None:
            self.fname = pfind('.', packagejson)
            if self.fname is None:  # pragma: nocover
                raise RuntimeError("I couldn't find a %s file" % packagejson)
        else:
            self.fname = os.path.join(basedir, packagejson)
        self.root = os.path.dirname(self.fname)
        self._package = None

    @property
    def package(self):
        if not self._package:
            with open(self.fname) as fp:
                self._package = json.loads(fp.read())
        return self._package

    def __setitem__(self, key, value):
        self.package[key] = value
        # print "PACKAGE:", self.package
        # print json.dumps(self.package, indent=4)
        json.dump(self.package, open(self.fname, 'w'), indent=4)

    def __getitem__(self, attr, default=None):
        try:
            return self.package[attr]
        except KeyError:
            # return default
            if default is not None:
                return default
            raise AttributeError(
                self.fname + " does not have an attribute named: " + attr)


def Package(*args, **kwargs):
    if PackageJson.exists():
        return PackageJson(*args, **kwargs)
    else:
        return PackageIni(*args, **kwargs)

