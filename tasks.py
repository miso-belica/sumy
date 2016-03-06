# -*- coding: utf-8 -*-

from invoke import task, run


@task
def clean():
    run("rm -rf .bumpversion.cfg .coverage dist build")


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
    run("bumpversion %s --config-file setup.cfg" % version)
    run("git rm .bumpversion.cfg")
    run("git commit --amend")
