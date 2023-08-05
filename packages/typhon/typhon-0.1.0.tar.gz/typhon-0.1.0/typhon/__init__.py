# -*- coding: utf-8 -*-

__version__ = '0.1.0'

from . import arts
from . import files
from . import utils


def _runtest():
    """Run all tests."""
    from os.path import dirname
    import nose
    loader = nose.loader.TestLoader(workingDir=dirname(__file__))
    return nose.run(testLoader=loader)

test = _runtest
