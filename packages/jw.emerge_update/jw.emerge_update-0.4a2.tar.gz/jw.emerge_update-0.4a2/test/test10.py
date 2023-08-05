"""
General run test
"""

import sys
from jw.emerge_update import main

def test10():
    sys.argv = ['main.py', '--dry-run']
    main.Main()
