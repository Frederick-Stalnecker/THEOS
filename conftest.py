"""
Root pytest configuration.

Adds ``code/`` and ``examples/`` to ``sys.path`` so the test suite can
import THEOS modules without a prior ``pip install -e .``.  When the
package *is* installed (``pip install -e ".[dev]"``) the path entries are
harmless duplicates.
"""

import os
import sys

_ROOT = os.path.dirname(__file__)

sys.path.insert(0, os.path.join(_ROOT, "code"))
sys.path.insert(0, os.path.join(_ROOT, "examples"))
