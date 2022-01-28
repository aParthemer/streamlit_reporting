

import streamlit as st
import pandas as pd

import CONSTANTS as C
from parse_config import ConfigParser
from report import get_joined_df,sliders_date
from upload_csv import validate_uploaded_files,display_upload_status

def cbox_display_state():
    cbox = st.checkbox(label="display state")
    if cbox:
        st.write(st.session_state)


def init_state():

    EXPECTED = [ConfigParser(C.DIR_TABLE_CONFIGS / "sk_transactions.yml"),
                ConfigParser(C.DIR_TABLE_CONFIGS / "sk_transaction_items.yml")]

    if "checked_file_ids" not in st.session_state:
        st.session_state["checked_file_ids"] = list()
    if "validated_dfs" not in st.session_state:
        st.session_state["validated_dfs"] = list()
    if "expected_configs" not in st.session_state:
        st.session_state["expected_configs"] = EXPECTED
    if "found_configs" not in st.session_state:
        st.session_state["found_configs"] = list()
    if "uploads_complete" not in st.session_state:
        st.session_state["uploads_complete"] = False
    if "df_joined" not in st.session_state:
        st.session_state["df_joined"] = None



if __name__ == '__main__':
    init_state()

    with st.sidebar:
        uploader = st.file_uploader(label="Upload CSV",
                                    accept_multiple_files=True,
                                    key="uploader",
                                    on_change=validate_uploaded_files,
                                    args=["uploader"])
        if st.session_state["uploads_complete"]:
            st.success("All files uploaded!")
        else:
            display_upload_status(st.session_state["expected_configs"])

        cbox_display_state()

    if (
            st.session_state["uploads_complete"] and
            st.session_state["df_joined"] is None
    ):

        dfs = tuple(st.session_state["validated_dfs"])
        configs = tuple(st.session_state["found_configs"])
        prefixes = tuple([c.column_prefix for c in configs])

        df_joined = get_joined_df(dfs=dfs,
                                  configs=configs,
                                  prefixes=prefixes,
                                  primary_key="transaction_id")
        df_joined["t_time"] = pd.to_datetime(df_joined["t_time"],
                                             infer_datetime_format=True)

        st.session_state["df_joined"] = df_joined

    if st.session_state["df_joined"] is not None:

        df_joined = st.session_state["df_joined"]

        with st.expander(label="Filter by Date",
                         expanded=False):
            df_by_date = sliders_date(df_joined,dt_column="t_time")

        if df_by_date is not None:

            st.dataframe(df_by_date)

















