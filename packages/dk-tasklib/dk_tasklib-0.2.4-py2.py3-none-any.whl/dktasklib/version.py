# -*- coding: utf-8 -*-
import re
import os
import hashlib
import textwrap

from dkfileutils.path import Path
from invoke import run, ctask as task
# from .subversion import get_svn_version
from .package import Package


@task(help=dict(
    dest_template="this filename template must contain '{version}'",
    kind="type of version number [pkg,hash]",
))
def add_version(ctx, source, dest_template, kind="pkg", force=None):
    """Add version number to a file (either pkg version, svn revision, or hash).

       Returns:
           (str) output file name
    """
    if kind == 'pkg' and not hasattr(ctx, 'pkg'):
        ctx.pkg = Package()
    if not hasattr(ctx, 'force'):
        ctx.force = bool(force)
    if force is not None:
        ctx.force = force
        
    if kind == "pkg":
        ver = ctx.pkg.version
    elif kind == "hash":
        ver = hashlib.md5(open(source).read()).hexdigest()
    # elif kind == "svn":
    #     ver = get_svn_version(source)
        
    ver_fname = dest_template.format(version=ver)

    if not ctx.force and os.path.exists(ver_fname):
        if open(source).read() != open(ver_fname).read():
            print """
            There is allready a file with the current version number,
            either run `inv version patch` to create a new version,
            or pass --force to the build command.
            """
    else:
        # copy file contents to versioned file name
        with open(ver_fname, 'wb') as fp:
            fp.write(open(source, 'rb').read())

    return ver_fname


@task
def version(ctx):
    vnum = Package().version
    print vnum
    return vnum


@task
def upversion(ctx, major=False, minor=False, patch=False):
    """Update package version (default patch-level increase).
    """
    if not (major or minor or patch):
        patch = True
    new_version = Package().upversion(major, minor, patch)
    print new_version
    return new_version


@task
def update_template_version(ctx, fname=None):
    """Update version number in include template.
    """
    if not hasattr(ctx, 'pkg'):
        ctx.pkg = Package()
    if not hasattr(ctx.pkg, 'update_template_version_fname'):
        _t = 'templates/{pkg.name}/{pkg.name}-css.html'.format(pkg=ctx.pkg)
        ctx.pkg.update_template_version_fname = _t
        
    fname = fname or ctx.pkg.update_template_version_fname

    if not os.path.exists(fname):
        Path(ctx.pkg.root).makedirs(Path(fname).dirname())
        with open(fname, 'w') as fp:
            fp.write(textwrap.dedent("""
            {% load staticfiles %}
            {% with "0.0.0" as version %}
                {# keep the above exactly as-is (it will be overwritten when compiling the css). #}
                {% with "PKGNAME/PKGNAME-"|add:version|add:".min.css" as app_path %}
                    {% if debug %}
                        <link rel="stylesheet" type="text/css" href='{% static "PKGNAME/PKGNAME.css" %}'>
                    {% else %}
                        <link rel="stylesheet" type="text/css" href="{% static app_path %}">
                    {% endif %}
                {% endwith %}
            {% endwith %}
            """).replace("PKGNAME", ctx.pkg.name))
            
    with open(fname, 'r') as fp:
        txt = fp.read()

    newtxt = re.sub(
        r'{% with "(\d+\.\d+\.\d+)" as version',
        '{{% with "{}" as version'.format(ctx.pkg.version),
        txt
    )
    with open(fname, 'w') as fp:
        fp.write(newtxt)
