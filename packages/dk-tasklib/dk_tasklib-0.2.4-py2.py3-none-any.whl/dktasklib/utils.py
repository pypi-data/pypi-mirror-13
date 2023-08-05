# -*- coding: utf-8 -*-
import inspect
import os
from contextlib import contextmanager

import sys

from dkfileutils.changed import changed

join = os.path.join
null = "NUL" if sys.platform == 'win32' else '/dev/null'
win32 = sys.platform == 'win32'


def switch_extension(fname, ext="", old_ext=None):
    """Switch file extension on `fname` to `ext`. Returns the resulting
       file name.

       Usage::

           switch_extension('a/b/c/d.less', '.css')
    
    """
    name, _ext = os.path.splitext(fname)
    if old_ext:
        assert old_ext == _ext
    return name + ext


def filename(fname):
    """Return only the file name (removes the path)
    """
    return os.path.split(fname)[1]


def min_name(fname, min='.min'):
    """Adds a `.min` extension before the last file extension.
    """
    name, ext = os.path.splitext(fname)
    return name + min + ext


def version_name(fname):
    """Returns a template string containing `{version}` in the correct
       place.
    """
    if '.min.' in fname:
        pre, post = fname.split('.min.')
        return pre + '-{version}.min.' + post
    else:
        return min_name(fname, '-{version}')
    

@contextmanager
def cd(directory):
    """Context manager to change directory.

       Usage::

           with cd('foo/bar'):
               # current directory is now foo/bar
           # current directory restored.

    """
    cwd = os.getcwd()
    os.chdir(directory)
    yield
    os.chdir(cwd)
