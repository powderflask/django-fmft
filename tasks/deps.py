from invoke import task


@task
def compile(c, upgrade=False, extras=(), output_file="requirements.txt", options=''):
    """ Run pip-compile with given CLI options """
    extras = ' '.join(f"--extra={e}" for e in extras)
    upgrade = '--upgrade' if upgrade else ''
    c.run(f"pip-compile --resolver=backtracking {upgrade} { extras } {options} -o { output_file } pyproject.toml")


@task
def compile_dev(c, upgrade=False, extras=(), output_file="requirements_dev.txt", options=''):
    """ pip-compile Dev requirements """
    compile(c, upgrade=upgrade, extras=extras, output_file=output_file, options='--all-extras '+options)


@task
def compile_docs(c, upgrade=False, extras=("docs", "fsm"), output_file="docs/requirements_docs.txt", options=''):
    """ pip-compile Docs requirements"""
    compile(c, upgrade=upgrade, extras=extras, output_file=output_file, options=options)


@task
def pin(c, dev=False, docs=False):
    """ Pin all core [and development] dependencies from pyproject.toml """
    print("Generating requirements files...")
    compile(c)
    if dev:
        compile_dev(c)
    if docs:
        compile_docs(c)
    print("Done.")


@task
def upgrade(c, dev=False, docs=False):
    """ Force update all core [and optional] dependencies in requirements files """
    print("Updating requirements files...")
    compile(c, upgrade=True)
    if dev:
        compile_dev(c, upgrade=True)
    if docs:
        compile_docs(c, upgrade=True)
    print("Done.")


@task
def install(c, dev=False):
    """ Install all core [and optional] dependencies """
    print("Installing dependencies...")
    c.run("pip-sync requirements.txt")
    if dev:
        c.run("pip-sync requirements_dev.txt")
    print("Done.")
