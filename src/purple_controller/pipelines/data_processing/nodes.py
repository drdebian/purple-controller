"""
This is a boilerplate pipeline 'data_processing'
generated using Kedro 0.17.6
"""

import pandas as pd
from typing import Dict, Any, Callable, Tuple


def get_ev_data(ev_data: pd.DataFrame, ev_config: Dict) -> pd.DataFrame:

    print(ev_data)
    print(ev_config)

    return ev_data
