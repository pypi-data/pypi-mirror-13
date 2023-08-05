# -*- coding: utf-8 -*-
import os
import sys

from dkfileutils.changed import Directory
from invoke import ctask as task, Collection

from dktasklib.executables import requires
from .package import Package
from .utils import switch_extension, filename, min_name, version_name, join
from .version import add_version, update_template_version

bootstrap = os.path.join(os.environ.get('SRV', ''), 'lib', 'bootstrap', 'less')


@requires('nodejs', 'npm', 'lessc')
def lessc(ctx,
          source, destination="",
          include_path=None,
          strict_imports=False,
          inline_urls=True,
          autoprefix=True,
          cleancss=True):
    """Run `lessc` with options.

       Args:
           source (str): the input file name
           destination (Optional[str]): the output filename (if not specified
                it will be the same as the input file name and a ``.css``
                extension).
           include_path (Optional[List[str]]): Optional list of directories
                to search to satisfy ``@import`` directives.
           strict_imports (bool): Re-fetch all imports.
           inline_urls (bool): Should ``@url(.../foo.png)`` be inlined?
           autoprefix (bool): Should the autoprefixer be run (last 4 versions)
           cleancss (bool): Should the css be minified?

       Returns:
           str: The output file name.

    """
    if include_path is None:
        include_path = []
    if not destination:
        destination = switch_extension(source, '.css', '.less')
    options = ""
    if getattr(ctx, 'verbose', False):  # pragma: nocover
        options += ' --verbose'
    if include_path:
        options += ' --include-path="%s"' % ';'.join(include_path)
    if strict_imports:
        options += " --strict-imports"
    if inline_urls:
        options += " --inline-urls"
    if autoprefix:
        options += ' --autoprefix="last 4 versions"'
    if cleancss:
        options += ' --clean-css="-b --s0 --advanced"'

    ctx.run("lessc {options} {source} {destination}".format(**locals()))
    return destination


def build_css(ctx,
              lessfile, dest,
              version='pkg',
              use_bootstrap=True,
              **kw):
    """Build a ``.less`` file into a versioned and minified ``.css`` file.

       Args:
           lessfile (str): input file name
           dest (str): output file name (should be the plain version of the
                output file name, ie. foo.css, not foo.min.css).
           version (str): the type of version number (pkg or hash)
           use_bootstrap (bool): Should Bootstrap be compiled in?

       Returns:
           str: output file name

    """
    path = kw.pop('path', [])
    if use_bootstrap:
        path.append(ctx.lessc.bootstrap_less_src)

    # foo.css -> foo.min.css
    minfname = min_name(dest)

    output_fname = lessc(
        ctx,
        lessfile,
        os.path.join('build', 'css', minfname),
        # minfname,
        include_path=path,
        strict_imports=True,
        inline_urls=True,
        autoprefix=True,
        cleancss=True,
    )
    
    return add_version(
        ctx,
        output_fname,
        version_name(output_fname),
        kind=version)


@task(
    default=True,
    post=[update_template_version],
    help={

    }
)
def build(ctx, force=False, verbose=False, src=None, dst=None, **kw):
    """Compile .less to .css  (pakage.json[build_less_input/output]
    """
    if not hasattr(ctx, 'pkg'):
        ctx.pkg = Package()
    if not hasattr(ctx.pkg, 'build_less_input'):
        ctx.pkg.build_less_input = src or 'less/{pkg.name}.less'.format(pkg=ctx.pkg)
    if not hasattr(ctx.pkg, 'build_less_output'):
        ctx.pkg.build_less_output = dst or 'static/{pkg.name}/{pkg.name}.css'.format(pkg=ctx.pkg)
    if not hasattr(ctx, 'force'):
        ctx.force = force
    if not hasattr(ctx, 'verbose'):
        ctx.verbose = verbose

    if ctx.verbose:  # pragma: nocover
        print 'build_less input: ', ctx.pkg.build_less_input
        print 'build_less output:', ctx.pkg.build_less_output

    dirname = os.path.dirname(ctx.pkg.build_less_input)

    if ctx.force or Directory(dirname).changed(glob='**/*.less'):
        build_css(
            ctx,
            ctx.pkg.build_less_input,
            ctx.pkg.build_less_output,
            version='pkg',
            **kw
        )   


less = Collection('lessc', build)
less.configure({
    'lessc': {
        'source': 'less/index.less',
        'target': '',
        'bootstrap_less_src': os.path.join(os.environ.get('BOOTSTRAPSRC', ''), 'less'),
    }
})
