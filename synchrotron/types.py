from typing import TypeAlias

import numpy as np
from numpy.typing import NDArray

from synchrotron.nodes import Input, Output

SignalBuffer: TypeAlias = NDArray[np.float32]
Port: TypeAlias = Input | Output
