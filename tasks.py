
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


@task
def docker(context):
    context.run("docker build --no-cache --rm=true --tag misobelica/sumy:latest -t misobelica/sumy:0.13.0 .")
    context.run("docker push misobelica/sumy --all-tags")
