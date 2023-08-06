# -*- coding: utf-8 -*-
import re
import os
import hashlib
import textwrap
import warnings

from dkfileutils.path import Path
from invoke import run, ctask as task, Collection
# from .subversion import get_svn_version
from .package import Package


@task(help=dict(
    source="",
    dest_template="this filename template must contain '{version}'",
    kind="type of version number [pkg,hash]",
))
def add_version(ctx, source, dest_template, kind="pkg", force=None):
    """Add version number to a file (either pkg version, svn revision, or hash).

       Returns:
           (str) output file name
    """
    if kind == "pkg":
        ver = ctx.pkg.version
    elif kind == "hash":
        ver = hashlib.md5(open(source).read()).hexdigest()
    # elif kind == "svn":
    #     ver = get_svn_version(source)
        
    ver_fname = dest_template.format(version=ver)

    if not force and os.path.exists(ver_fname):
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


@task(
    aliases=['ver'],
    autoprint=True,     # print return value
)
def version(ctx):
    "Print this package's version number."
    return Package().version


def files_with_version_numbers():
    pkg = Package()
    root = pkg.root
    default = {
        root / 'setup.py',
        root / 'package.json',
        root / 'package.ini',
        root / 'package.yaml',
        root / 'docs' / 'conf.py',
        pkg.sourcedir / '__init__.py',
        pkg.sourcedir / '_version.py',
    }
    return default


def _replace_version(fname, cur_version, new_version):
    if not fname.exists():
        return False

    with open(fname, 'rb') as fp:
        txt = fp.read()

    if cur_version not in txt:
        # warnings.warn("Did not find %r in %r" % (cur_version, fname))
        return False
    occurences = txt.count(cur_version)
    if occurences > 2:
        warnings.warn(
            "Found version string (%r) multiple times in %r, skipping" % (
                cur_version, fname
            )
        )
    txt = txt.replace(cur_version, new_version)

    with open(fname, 'wb') as fp:
        fp.write(txt)
    return 1


@task(autoprint=True)
def upversion(ctx, major=False, minor=False, patch=False):
    """Update package version (default patch-level increase).
    """
    pkg = Package()
    if not (major or minor or patch):
        patch = True  # pragma: nocover
    txt_version = pkg.version
    cur_version = [int(n, 10) for n in txt_version.split('.')]
    if major:
        cur_version[0] += 1
        cur_version[1] = 0
        cur_version[2] = 0
    elif minor:
        cur_version[1] += 1
        cur_version[2] = 0
    elif patch:
        cur_version[2] += 1
    new_version = '.'.join([str(n) for n in cur_version])

    changed = 0
    for fname in files_with_version_numbers():
        changed += _replace_version(fname, txt_version, new_version)
    if changed == 0:
        warnings.warn("I didn't change any files...!")
    print "changed %d files" % changed
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
                {% with app_path="PKGNAME/PKGNAME-"|add:version|add:".min.css" %}
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

ns = Collection(
    'version',
    add_version,
    version,
    upversion,
    update_template_version
)
ns.configure({
    'force': False,
    'pkg': {
        'name': '<package-name>',
        'version': '<version-string>',
    },
})
