# -*- coding: utf-8 -*-

from invoke import task, run


@task
def clean():
    run("rm -rf .coverage dist build")


@task(clean, default=True)
def test():
    run("py.test")


@task(test)
def install():
    run("pandoc --from=markdown --to=rst README.md -o README.rst")
    run("python setup.py develop")


@task(test)
def release():
    run("pandoc --from=markdown --to=rst README.md -o README.rst")
    run("python setup.py register sdist bdist_wheel")
    run("twine upload dist/*")


@task(test)
def bump(version="patch"):
    run("bumpversion %s" % version)
    run("git commit --amend")
