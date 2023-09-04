from invoke import Collection

from . import clean, deps, docs, pypi

namespace = Collection(clean, deps, docs, pypi)
