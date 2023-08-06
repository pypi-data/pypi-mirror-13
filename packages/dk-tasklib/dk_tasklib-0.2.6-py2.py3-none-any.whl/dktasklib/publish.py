# -*- coding: utf-8 -*-


from invoke import ctask as task

from . import Package


@task(
    default=True
)
def publish(ctx):
    """Publish to PyPi
    """
    pkg = Package()
    with pkg.root.cd():
        ctx.run("python setup.py sdist bdist_wheel upload")
        ctx.run("python setup.py upload_docs")
