try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

from invoke import task, Collection
from . import clean, docs, pypi


@task
def install_deps(c):
    # Load pyproject.toml file
    with open("pyproject.toml", "r") as f:
        pyproject = tomllib.load(f)

    # Install core dependencies
    if "dependencies" in pyproject["project"]:
        for dep in pyproject["project"]["dependencies"]:
            c.run(f"python -m pip install {dep}")

    # Install optional dependencies
    if "optional-dependencies" in pyproject["project"]:
        for opt_dep_list in pyproject["project"]["optional-dependencies"].values():
            for opt_dep in opt_dep_list:
                c.run(f"python -m pip install {opt_dep}")

    print("Dependencies installed successfully.")


namespace = Collection(clean, docs, pypi)
namespace.add_task(install_deps)
