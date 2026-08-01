
from invoke import task


@task
def clean(context):
    context.run("rm -rf dist build .coverage .pytest_cache .mypy_cache")


@task(clean, default=True)
def test(context):
    context.run("uv run pytest")


@task(test)
def install(context):
    context.run("uv sync --all-extras")


@task(test)
def release(context):
    context.run("uv build")
    context.run("uv publish")


@task(test)
def bump(context, version="patch"):
    context.run(f"bumpversion {version}")
    context.run("git commit --amend")

@task
def docker(context):
    context.run("docker build --no-cache --rm=true --tag misobelica/sumy:latest -t misobelica/sumy:0.12.0 .")
    context.run("docker push misobelica/sumy --all-tags")
