from datetime import datetime
from typing import Union, List, Dict, Optional, Tuple

import pandas as pd
from pandasql import sqldf
import streamlit as st

from parse_config import ConfigParser, detect_config
from style import highlight_columns

"""
Given both `transactions` and `transaction items`

- join dataframes on transaction id (transaction items LEFT JOIN transactions)

"""

def read_csv(csv) -> pd.DataFrame:
    df = pd.read_csv(csv)
    return df


def apply_schema(df: pd.DataFrame,
                 config: ConfigParser) -> pd.DataFrame:
    try:
        df = config.apply_column_mapper(df)
        df = config.apply_type_conversions(df)
    except:
        raise
    return df

def apply_column_prefixes(df: pd.DataFrame,
                          prefix: str):
    col_mapper = {}
    for col in df.columns:
        new_col = None
        if not col.startswith(prefix):
            new_col = prefix + col

        if new_col is not None:
            col_mapper[col] = new_col
        else:
            col_mapper[col] = col

    df = df.rename(columns=col_mapper)

    return df


def join_dfs(dfs: Tuple[pd.DataFrame, pd.DataFrame],
             prefixes: Tuple[str, str],
             primary_key: str) -> pd.DataFrame:
    dfs_prefixed = []
    columns_strings = []
    for df, prefix in zip(dfs, prefixes):
        df_prefixed = apply_column_prefixes(df, prefix)
        dfs_prefixed.append(df_prefixed)

        dot_prefix = prefix.replace("_", ".")
        column_string = ", ".join([dot_prefix + col for col in df_prefixed.columns])
        columns_strings.append(column_string)

    keys_prefixed = [prefix + primary_key for prefix in prefixes]
    df0 = dfs_prefixed[0]
    df1 = dfs_prefixed[1]

    column_string = ", ".join(columns_strings)

    q = f"""
    SELECT {column_string}
    FROM df0 AS {prefixes[0][:-1]}
    INNER JOIN df1 AS {prefixes[1][:-1]}
    ON {keys_prefixed[0]} = {keys_prefixed[1]};
    """

    df_joined = sqldf(q, locals())

    return df_joined


def get_joined_df(dfs: Tuple[pd.DataFrame, pd.DataFrame],
                  configs: Tuple[ConfigParser, ConfigParser],
                  prefixes: Tuple[str, str],
                  primary_key: str):
    """
    Config has already been validated.
    """

    _dfs = []
    for df, config in zip(dfs, configs):
        _df = df
        _df = apply_schema(_df, config)
        _dfs.append(_df)

    joined_df = join_dfs(dfs=tuple(_dfs),
                         prefixes=tuple(prefixes),
                         primary_key=primary_key)

    joined_df["t_time"] = pd.to_datetime(joined_df["t_time"],
                                         infer_datetime_format=True)
    joined_df["date"] = joined_df["t_time"].dt.date

    return joined_df


#### GIVEN MAIN_DF ####

def filter_by_date(df: pd.DataFrame,
                   dt_column: str,
                   start: datetime,
                   end: datetime) -> pd.DataFrame:
    start_date = start.date()
    end_date = end.date()

    mask_ = (df[dt_column].dt.date >= start_date) & (df[dt_column].dt.date <= end_date)
    df_filtered = df[mask_]

    return df_filtered


def cb_slider_dates(key: str, df: pd.DataFrame, dt_column: str):

    start, end = st.session_state[key]
    _df = df[
        (df[dt_column].dt.date >= start) &
        (df[dt_column].dt.date <= end)
        ]

    st.session_state["df_by_date"] = _df
    st.session_state["date_expander_state"] = True


def slider_dates(df: pd.DataFrame,
                 dt_column: str) -> None:
    dates = pd.Series(df[dt_column].dt.date.unique())
    dates = dates.sort_values()

    start, end = st.select_slider(
        "Select a date range",
        options=dates,
        value=(dates.iloc[0], dates.iloc[-1]),
        key="date_slider",
        on_change=cb_slider_dates,
        kwargs={"key": "date_slider",
                "df": df,
                "dt_column": dt_column}
    )
    _df_by_date = st.session_state.get("df_by_date")
    if _df_by_date is not None:
        n_rows = len(_df_by_date.index)
    else:
        n_rows = len(df.index)
    st.caption(f"There are {n_rows} records between `{start}` and `{end}`")

def sbox_filter_by_column_value(df: pd.DataFrame,
                                column: str,
                                label: Optional[str] = None):
    unique_values = df[column].unique()

    if label is None:
        label = f"Filter by {column}"

    option = st.selectbox(label=label,
                          options=unique_values)

    df_filtered = df[df[column] == option]

    return df_filtered
