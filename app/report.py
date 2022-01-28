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


@st.cache(suppress_st_warning=True)
def read_csv(csv) -> pd.DataFrame:
    df = pd.read_csv(csv)
    return df


@st.cache(suppress_st_warning=True)
def apply_schema(df: pd.DataFrame,
                 config: ConfigParser) -> pd.DataFrame:
    try:
        df = config.apply_column_mapper(df)
        df = config.apply_type_conversions(df)
    except:
        raise
    return df


@st.cache(suppress_st_warning=True)
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


@st.cache(suppress_st_warning=True)
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
        _df = apply_schema(df, config)
        _dfs.append(_df)

    joined_df = join_dfs(dfs=tuple(_dfs),
                         prefixes=tuple(prefixes),
                         primary_key=primary_key)

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


def sliders_date(df: pd.DataFrame,
                 dt_column: str) -> pd.DataFrame:

    dates = pd.Series(df[dt_column].dt.date.unique())
    dates = dates.sort_values()

    start_slider = st.select_slider(
        label="Select start date",
        options=dates.tolist()
    )


    end_dates = dates[dates >= start_slider]
    end_slider = st.select_slider(
        label="Select end date",
        options=end_dates.tolist()
    )

    btn_apply_filter = st.button(label="Apply date filter",)

    if btn_apply_filter:
        df_ = df[
            (df[dt_column].dt.date >= start_slider) &
            (df[dt_column].dt.date <= end_slider)
            ]
        start_ = start_slider
        end_ = end_slider
        if df_ is not None:
            n_rows = len(df_.index)
            st.caption(f"{n_rows} records between `{start_}` and `{end_}`")
            return df_

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


if __name__ == '__main__':
    import CONSTANTS as C
    from parse_config import ConfigParser

    csv_tr = C.DIR_DATA / "sk_transactions_2021-10-01_2021-12-10.csv"
    csv_tr_items = C.DIR_DATA / "sk_transaction_items_2021-10-01_2021-12-10.csv"

    df_tr = pd.read_csv(csv_tr)
    df_tr_items = pd.read_csv(csv_tr_items)

    cfg_tr = ConfigParser(C.DIR_TABLE_CONFIGS / "sk_transactions.yml")
    cfg_tr_items = ConfigParser(C.DIR_TABLE_CONFIGS / "sk_transaction_items.yml")

    main_df = get_joined_df(dfs=(df_tr, df_tr_items),
                            configs=(cfg_tr, cfg_tr_items),
                            prefixes=("t_", "ti_"),
                            primary_key="transaction_id")
    main_df["t_time"] = pd.to_datetime(main_df["t_time"],
                                         infer_datetime_format=True)

    df = sliders_date(main_df,"t_time")
    if df is not None:
        st.dataframe(df)
