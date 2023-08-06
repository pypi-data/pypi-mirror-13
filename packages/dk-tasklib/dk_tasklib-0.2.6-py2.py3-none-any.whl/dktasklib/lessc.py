# -*- coding: utf-8 -*-
import os

from dkfileutils.changed import Directory
from dkfileutils.path import Path
from invoke import ctask as task, Collection

from dktasklib.executables import requires
from .utils import switch_extension, filename
from dktasklib.version import min_name, version_name
from .version import add_version, update_template_version


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


@task(
    default=True,
    post=[update_template_version],
    help={
        'input_dir': 'directory to search for input_fname',
        'input_fname': 'input filename ({pkg.name}.less)',
        'output_dir': 'directory to place output_fname',
        'output_fname': 'output filename ({pkg.name}.css)',
        'force': 'Rebuild without cache.'
    }
)
def build_less(ctx,
               input_dir=None,
               input_fname=None,
               output_dir=None,
               output_fname=None,
               version='pkg',
               use_bootstrap=True,
               force=False,
               **kw):
    """Build a ``.less`` file into a versioned and minified ``.css`` file.

       Args:
           input_fname (str): input file name
           output_fname (str): output file name (should be the plain version of the
                output file name, ie. foo.css, not foo.min.css).
           version (str): the type of version number (pkg or hash)
           use_bootstrap (bool): Should Bootstrap be compiled in?
           force (bool): Rebuild even if nothing has changed.

       Returns:
           str: output file name

    """
    src = input_fname or ctx.lessc.input_fname.format(**ctx)
    dst = output_fname or ctx.lessc.output_fname.format(**ctx)

    input_dir = input_dir or ctx.lessc.input_dir.format(**ctx)
    output_dir = output_dir or ctx.lessc.output_dir.format(**ctx)

    if not force and not Directory(input_dir).changed(glob='**/*.less'):
        print """
        No changes detected in {input_dir}/{glob}, add --force
        to less file(s) build anyway.
        """.format(input_dir=input_dir, glob='**/*.less')
        return

    path = kw.pop('path', [])
    if (use_bootstrap or ctx.lessc.use_bootstrap) and ctx.bootstrap.src:
        path.append(ctx.bootstrap.src)

    # foo.css -> foo.min.css
    minfname = min_name(dst)
    buildname = lessc(
        ctx,
        os.path.join(input_dir, src),
        os.path.join(ctx.lessc.build_dir, minfname),
        include_path=path,
        strict_imports=True,
        inline_urls=True,
        autoprefix=True,
        cleancss=True,
    )

    outname = version_name(buildname)
    versioned_name = add_version(ctx,
                                 buildname, outname,
                                 kind=version,
                                 force=force)
    out_name = os.path.join(output_dir, filename(versioned_name))
    if force or not os.path.exists(out_name):
        Path(output_dir).makedirs()
        ctx.run('cp {src} {dst}'.format(
            src=versioned_name,
            dst=out_name
        ))
    else:
        print """
        Filename already exists, add --force or call upversion: {}
        """.format(out_name)
    return out_name


ns = Collection('lessc', build_less)
ns.configure({
    'force': False,
    'pkg': {
        'name': '<package-name>',
        'version': '<version-string>',
    },
    'bootstrap': {
        'src': os.path.join(os.environ.get('BOOTSTRAPSRC', ''), 'less'),
    },
    'lessc': {
        'use_bootstrap': False,
        'build_dir': 'build/css',
        'input_dir': 'less',
        'input_fname': '{pkg.name}.less',
        'output_dir': 'static/{pkg.name}/css/',
        'output_fname': '{pkg.name}.css',
    }
})
