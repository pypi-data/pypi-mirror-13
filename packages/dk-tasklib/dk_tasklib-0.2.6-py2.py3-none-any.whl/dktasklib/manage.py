# -*- coding: utf-8 -*-
import os
from invoke import ctask as task, run
from .utils import cd
from .package import Package


DEFAULT_SETTINGS_MODULE = 'datakortet.settings'
DEFAULT_MANAGE_PY_PATH = os.path.join(os.environ.get('SRV', ''), 'src', 'datakortet')


@task
def manage(ctx, cmd, settings=None, manage_path=None):
    """Run manage.py with `settings` in a separate process.
    """
    # os.environ['DJANGO_SETTINGS_MODULE'] = settings or DEFAULT_SETTINGS_MODULE
    with cd(manage_path or DEFAULT_MANAGE_PY_PATH):
        run("python manage.py " + cmd)


@task
def collectstatic(ctx, verbose=False):
    "Run collectstatic with settings from package.json ('django_settings_module')"
    if not hasattr(ctx, 'pkg'):
        ctx.pkg = Package()
    if not hasattr(ctx, 'verbose'):
        ctx.verbose = verbose

    try:
        settings = ctx.pkg.django_settings_module
    except AttributeError:
        settings = DEFAULT_SETTINGS_MODULE
    if ctx.verbose:
        print "using settings:", settings
    manage(ctx, "collectstatic --noinput", settings)
