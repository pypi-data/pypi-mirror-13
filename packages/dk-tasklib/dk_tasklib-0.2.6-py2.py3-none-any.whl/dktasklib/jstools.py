# -*- coding: utf-8 -*-
import os
import textwrap

from invoke import ctask as task, Collection

from dktasklib import runners
from dktasklib.executables import requires
from dktasklib.utils import cd


def ensure_package_json(ctx):
    """Is this a node package?
    """
    package_json = os.path.join(ctx.pkg.root, 'package.json')
    if not os.path.exists(package_json):
        print "Missing package.json file, creating default version.."
        with cd(ctx.pkg.root):
            ctx.run("npm init -f")


def ensure_babelrc(ctx):
    """babel needs a .babelrc file to do any work.
    """
    babelrc = os.path.join(ctx.pkg.root, '.babelrc')
    if not os.path.exists(babelrc):
        print 'Misssing %s (creating default version)' % babelrc
        with open(babelrc, 'w') as fp:
            fp.write(textwrap.dedent("""
            {
                "presets": ["es2015"]
            }
            """))


def ensure_node_modules(ctx):
    """Has node init been called? (if not call it).
    """
    node_modules = os.path.join(ctx.pkg.root, 'node_modules')
    if not os.path.exists(node_modules):
        with cd(ctx.pkg.root):
            ctx.run("npm install --no-color")


def ensure_es2015(ctx):
    if 'babel-preset-es2015' not in runners.run("npm ls --depth=0 babel-preset-es2015 --no-color"):
        print "didn't find babel-preset-es2015, installing it.."
        with cd(ctx.pkg.root):
            ctx.run("npm install babel-preset-es2015 --save-dev")


@requires('babel', 'nodejs')
@task
def babel(ctx, source, dest, source_maps=True):
    """
    --source-maps --out-file $ProjectFileDir$/$ProjectName$/static/$ProjectName$/$FileNameWithoutExtension$.js $FilePath$
    """
    ensure_package_json(ctx)
    ensure_node_modules(ctx)
    ensure_es2015(ctx)
    ensure_babelrc(ctx)

    options = ""
    if source_maps:
        options += " --source-maps"

    ctx.run("babel {options} --out-file {dest} {source}".format(**locals()))


@requires('browserify', 'nodejs')
@task
def browserify(ctx, source, dest, require=(), external=(), entry=None):
    """
    Run ``browserify``

    Args:
        ctx (pyinvoke.Context):  context
        source (str):            root source file
        dest (str):              path/name of assembled file
        require (iterable):
        external:
        entry:

    Returns:
        None

    """
    ensure_package_json(ctx)
    ensure_node_modules(ctx)

    options = ""
    for r in require:
        options += ' -r "%s"' % r
    for e in external:
        options += ' -x "%s"' % e
    if entry:
        options += ' -e "%s"' % entry
    cmd = "browserify {source} -o {dest} {options}".format(**locals())
    ctx.run(cmd)


ns = Collection(babel, browserify)
ns.configure({
    'static': 'static/{pkg.name}'
})
