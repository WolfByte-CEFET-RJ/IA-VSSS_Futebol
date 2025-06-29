import math
import os
from collections.abc import Iterable

class Colors:
    def __init__(self):
        self.RED = '#ff0000'
        self.GREEN = '#00ff00'
        self.BLUE = '#0000ff'
        self.YELLOW = '#ffff00'
        self.PURPLE = '#aa00ff'
        self.ORANGE = '#ffaa00'
        self.CYAN = '#00aaff'
        self.PINK = '#ff00aa'

def to_scale(m):
    s = int(os.environ.get('V3S_SIM_DPI_SCALING_FACTOR'))*int(os.environ.get('V3S_SIM_PSI_SCALING_FACTOR'))
    res = s*m if not isinstance(m, Iterable) else [s*mm for mm in m]
    return res

def interrupt():
    assert False, 'Interrupted by Assertion.'