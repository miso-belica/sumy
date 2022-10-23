# -*- coding: utf-8 -*-

from invoke import task


@task
def clean(context):
    context.run("rm -rf dist build .coverage .pytest_cache .mypy_cache")


@task(clean, default=True)
def test(context):
    context.run("pytest")


@task(test)
def install(context):
    context.run("python setup.py develop")


@task(test)
def release(context):
    context.run("python setup.py register sdist bdist_wheel")
    context.run("twine upload dist/*")


@task(test)
def bump(context, version="patch"):
    context.run("bumpversion %s" % version)
    context.run("git commit --amend")

@task
def docker(context):
    context.run("docker build --no-cache --rm=true --tag misobelica/sumy:latest -t misobelica/sumy:0.11.0 .")
    context.run("docker push misobelica/sumy --all-tags")
