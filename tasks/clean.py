from invoke import task


@task(name="build")
def clean_build(c):
    """ Remove build artifacts """
    print("Cleaning build artifacts...")
    c.run("rm -fr build/")
    c.run("rm -fr dist/")
    c.run("rm -fr .eggs/")
    c.run("find . -name '*.egg-info' -exec rm -fr {} +")
    c.run("find . -name '*.egg' -exec rm -f {} +")
    print("Done.")


@task(name="cache")
def clean_cache(c):
    """ Remove Python file artifacts """
    print("Cleaning Python file artifacts...")
    c.run("find . -name '*.pyc' -exec rm -f {} +")
    c.run("find . -name '*.pyo' -exec rm -f {} +")
    c.run("find . -name '*~' -exec rm -f {} +")
    c.run("find . -name '__pycache__' -exec rm -fr {} +")
    print("Done.")


@task(name="test")
def clean_test(c):
    """ Remove test and coverage artifacts """
    print("Cleaning test/coverage artifacts...")
    c.run("rm -fr .tox/")
    c.run("rm -f .coverage")
    c.run("rm -fr htmlcov/")
    c.run("rm -fr .pytest_cache")
    print("Done.")


@task(name="all", pre=[clean_build, clean_cache, clean_test])
def clean_all(c):
    """ Remove all build, test, coverage, and Python artifacts """
    print("All clean! :)")
