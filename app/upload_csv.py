from typing import List

import pandas as pd
import streamlit as st

from parse_config import detect_config, ConfigParser
import CONSTANTS as C

def validate_uploaded_files(uploader_key: str):

    expected_configs = st.session_state["expected_configs"]
    uploaded_files = st.session_state[uploader_key]

    for file in uploaded_files:
        if file.id not in st.session_state["checked_file_ids"]:
            st.session_state["checked_file_ids"].append(file.id)

            try:
                df = pd.read_csv(file)
                config = detect_config(df,expected_configs)
            except:
                raise

            if config not in st.session_state["found_configs"]:
                st.session_state["found_configs"].append(config)
                st.session_state["validated_dfs"].append(df)

    if all([c in st.session_state["found_configs"] for c in expected_configs]):
        st.session_state["uploads_complete"] = True
    else:
        st.session_state["uploads_complete"] = False

def display_upload_status(expected_configs: List[ConfigParser]):

    found = [c.table_name for c in expected_configs if c in st.session_state["found_configs"]]
    found_str = "".join(["\n- " + t for t in found])

    not_found = [c.table_name for c in expected_configs if c not in st.session_state["found_configs"]]
    not_found_str = "".join(["\n- " + t for t in not_found])

    st.warning(f"Please upload: {not_found_str}")
    st.success(f"Uploaded: {found_str}")

if __name__ == '__main__':

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

    uploader = st.file_uploader(label="Upload CSV",
                                accept_multiple_files=True,
                                key="uploader",
                                on_change=validate_uploaded_files,
                                args=["uploader"])

    if st.session_state["uploads_complete"]:
        st.success("yay")
    else:
        display_upload_status(st.session_state["expected_configs"])

