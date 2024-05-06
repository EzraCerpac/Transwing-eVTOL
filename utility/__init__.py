from pathlib import Path

import pandas as pd
import pint

if pd.__version__ == "2.0.0rc0":
    import pyarrow

    pd.options.mode.dtype_backend = 'pyarrow'
    float_type = pd.ArrowDtype(pyarrow.float64())
    int_type = pd.ArrowDtype(pyarrow.int64())
    bool_type = pd.ArrowDtype(pyarrow.bool_())
else:
    float_type = 'float64'
    int_type = 'int64'
    bool_type = 'bool'

raw_data_path = Path(__file__).parent.parent.parent / "data"
save_path = Path(__file__).parent.parent / "save"
save_path.mkdir(parents=True, exist_ok=True)

ureg = pint.UnitRegistry(system="mks")
Q_ = ureg.Quantity
ureg.define('fraction = [] = frac')
ureg.define('percent = 1e-2 frac = %')
ureg.define('ddmmyy = [] = ddmmyy')
