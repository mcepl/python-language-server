# Copyright 2017 Palantir Technologies, Inc.
import logging
import os
import sys

import pluggy

logging.basicConfig(format='%(levelname)s:%(funcName)s:%(message)s',
                    level=logging.DEBUG)

# from importlib.resources import version

# __version__ = pkg_resources.get_distribution('rope-language-server').version
__version__ = 0.0

ROLS = "rols"

hookspec = pluggy.HookspecMarker(ROLS)
hookimpl = pluggy.HookimplMarker(ROLS)

IS_WIN = os.name == "nt"
