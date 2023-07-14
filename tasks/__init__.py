from invoke import Collection, task

from . import clean, deps, docs, pypi

namespace = Collection(clean, deps, docs, pypi)
