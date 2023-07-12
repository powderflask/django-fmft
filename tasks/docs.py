from invoke import task


def make(c, command):
    c.run("cd docs")
    c.run(f"make {command}")


@task
def clean(c):
    """ Clean up docs directory """
    make(c, "clean")


@task(clean)
def build(c):
    """ Clean up and build Sphinx docs """
    make(c, "html")


@task(build)
def release(c):
    """ Push docs to GitHub, triggering webhook to build Read The Docs """
    c.run("git push")
