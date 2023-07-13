from invoke import task

from . import docs as docs_task


@task
def clean(c, docs=False):
    """Clean up dist [and docs] directory"""
    c.run("rm -fr ./dist/*")
    if docs:
        docs_task.clean(c)


@task(clean)
def build(c, docs=False):
    """Clean up and build a new distribution [and docs]"""
    c.run("python -m build")
    c.run("invoke clean.all")
    if docs:
        docs_task.build(c)


@task
def get_version(c):
    """Return current version using bumpver"""
    c.run("bumpver show --no-fetch")


@task
def upload(c, repo="testpypi"):
    """Upload build to given PyPI repo"""
    c.run(f"twine upload --repository {repo} dist/*")


@task(help={"dist": "Name of distribution file under dist/ directory to check."})
def check(c, dist):
    """Twine check the given distribution"""
    c.run(f"twine check dist/{dist}")


@task(help={"repo": "Specify:  pypi  for a production release."})
def release(c, repo="testpypi"):
    """Build release and upload to PyPI"""
    print("Fetching version...")
    get_version(c)
    if input("Continue? (y/n): ").lower()[0] != "y":
        print("Release aborted.")
        exit(0)
    print("Building new release...")
    build(c)
    print(f"Uploading release to {repo}...")
    upload(c, repo)
    print("Success! Your package has been released.")
