from typing import List

import numpy as np
import pandas as pd
from pandas.io.formats.style import Styler

import streamlit as st

from functools import partial

def highlight_columns(df: pd.DataFrame,
                      columns: List[str],
                      color: str = "#E7DBD9") -> Styler:

    df = df.style.highlight_between(subset=columns,
                                    color=color)

    return df

if __name__ == '__main__':
    data = pd.DataFrame(np.random.randn(5, 3), columns=list('ABC'))

    df = highlight_columns(data,["B"])



