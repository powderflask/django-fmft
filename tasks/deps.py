from invoke import task


@task
def pin(c, optional=False, docs=False):
    """Pin all core [and optional] dependencies from pyproject.toml"""
    print("Generating requirements files...")
    c.run("pip-compile --resolver=backtracking -o requirements.txt pyproject.toml")
    if optional:
        c.run(
            "pip-compile --resolver=backtracking --all-extras -o requirements_dev.txt pyproject.toml"
        )
    if docs:
        c.run(
            "pip-compile --resolver=backtracking --extra=docs -o docs/requirements_docs.txt pyproject.toml"
        )
    print("Done.")


@task
def upgrade(c, optional=False, docs=False):
    """Force update all core [and optional] dependencies in requirements files"""
    print("Updating requirements files...")
    c.run(
        "pip-compile --resolver=backtracking --upgrade -o requirements.txt pyproject.toml"
    )
    if optional:
        c.run(
            "pip-compile --resolver=backtracking --all-extras --upgrade -o requirements_dev.txt pyproject.toml"
        )
    if docs:
        c.run(
            "pip-compile --resolver=backtracking --extra=docs --upgrade -o docs/requirements_docs.txt pyproject.toml"
        )
    print("Done.")


@task
def install(c, optional=False):
    """Install all core [and optional] dependencies"""
    print("Installing dependencies...")
    c.run("pip-sync requirements.txt")
    if optional:
        c.run("pip-sync requirements_dev.txt")
    print("Done.")
