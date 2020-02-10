# Copyright 2017 Palantir Technologies, Inc.
import os
import sys
import pluggy
from ._version import get_versions

__version__ = get_versions()['version']
del get_versions

PYLS = 'pyls'

hookspec = pluggy.HookspecMarker(PYLS)
hookimpl = pluggy.HookimplMarker(PYLS)

IS_WIN = os.name == 'nt'
