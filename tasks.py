# -*- coding: utf-8 -*-

from invoke import task


@task
def clean(context):
    context.run("rm -rf .coverage dist build")


@task(clean, default=True)
def test(context):
    context.run("py.test")


@task(test)
def install(context):
    context.run("python setup.py develop")


@task(test)
def release(context):
    context.run("python setup.py register sdist bdist_wheel")
    context.run("twine upload dist/*")


@task(test)
def bump(context, version="patch"):
    context.run("pandoc --from=markdown --to=rst README.md -o README.rst")
    context.run("bumpversion %s" % version)
    context.run("git commit --amend")
