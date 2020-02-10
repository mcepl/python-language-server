# Copyright 2017 Palantir Technologies, Inc.
import os
import sys

import pluggy

# from importlib.resources import version

# __version__ = pkg_resources.get_distribution('rope-language-server').version
__version__ = 0.0

PYLS = "pyls"

hookspec = pluggy.HookspecMarker(PYLS)
hookimpl = pluggy.HookimplMarker(PYLS)

IS_WIN = os.name == "nt"
