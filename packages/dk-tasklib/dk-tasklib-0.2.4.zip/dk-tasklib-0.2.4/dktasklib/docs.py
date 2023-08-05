# -*- coding: utf-8 -*-

import os
import webbrowser
from os.path import join

from invoke import ctask as task, Collection


# Underscored func name to avoid shadowing kwargs in build()
@task(name='clean')
def _clean(ctx):
    """Nuke docs build target directory so next build is clean.
    """
    builddir = ctx.docs.builddir
    if os.path.exists(builddir) and len(os.listdir(builddir)) > 0:
        ctx.run("rm -rf {0}/*".format(builddir))


# Ditto
@task(name='browse')
def _browse(ctx):  # pragma: nocover
    """Open build target's index.html in a browser (using the :py:mod:`webbrowser` module).
    """
    index = join(ctx.docs.builddir, ctx.docs.target_file)
    webbrowser.open_new(index)


@task(default=True, help={
    'opts': "Extra sphinx-build options/args",
    'clean': "Remove build tree before building",
    'browse': "Open docs index in browser after building",
    'warn': "Build with stricter warnings/errors enabled",
    'builder': "Builder to use; defaults tto html",
    'force': "Force re-reading of all files (ignore cache)",
})
def build(ctx, clean=False, browse=False, warn=False,
          builder='html',
          force=True,
          opts=""):
    """
    Build the project's Sphinx docs.
    """
    if clean:
        _clean(ctx)
    if opts is None:  # pragma: nocover
        opts = ""
    opts += " -b %s" % builder
    if warn:
        opts += " -n -W"
    if force:
        opts += " -a -E"
    cmd = "sphinx-build {opts} {ctx.docs.source} {ctx.docs.builddir}".format(
        opts=opts, ctx=ctx)
    ctx.run(cmd)
    if browse:  # pragma: nocover
        _browse(ctx)


@task
def tree(ctx):
    """Display the docs tree.
    """
    ignore = ".git|*.pyc|*.swp|dist|*.egg-info|_static|_build|_templates"
    ctx.run('tree -Ca -I "{0}" {1}'.format(ignore, ctx.docs.source))


# Vanilla/default/parameterized collection for normal use
docs = Collection('docs', _clean, _browse, build, tree)
docs.configure({
    'docs': {
        'source': 'docs',
        'builddir': join('build', 'docs'),
        'target_file': 'index.html',
    }
})
