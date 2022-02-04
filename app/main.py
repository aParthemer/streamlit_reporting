import streamlit as st
import pandas as pd

import CONSTANTS as C
from parse_config import ConfigParser
from transform import get_joined_df, slider_dates, sbox_filter_by_column_value
from upload_csv import validate_uploaded_files, display_upload_status
import report as rpt
from charts import bar_chart, sbox_bar_chart, chart_layout


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

    if "date_expander_state" not in st.session_state:
        st.session_state["date_expander_state"] = False
    if "df_by_date" not in st.session_state:
        st.session_state["df_by_date"] = None

    if "selected_report" not in st.session_state:
        st.session_state["selected_report"] = ""


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

#### GIVEN JOINED DATAFRAME ####

if st.session_state["df_joined"] is not None:

    df_joined = st.session_state["df_joined"]

    _expanded = st.session_state["date_expander_state"]
    with st.expander(label="Filter by Date",expanded=_expanded):
        slider_dates(df_joined, dt_column="t_time")

    # st.dataframe(df_by_date)
    with st.expander(label="Select a Report"):
        sbox_reports = st.selectbox(label="Select a report to generate",
                                    options=[
                                        "",
                                        "Ticketing by Event"
                                    ],
                                    index=0,
                                    key="selected_report")

#### GIVEN: DF BY DATE / SELECTED REPORT

_df_by_date = st.session_state.get("df_by_date")
_selected_report = st.session_state.get("selected_report")
if (
    _df_by_date is not None and
    _selected_report != ""
):
    if _selected_report == "Ticketing by Event":
        st.markdown("## Ticketing by Event")

        event_type = st.selectbox(label="Select event type",
                                  options=["","Show","Jam"],
                                  index=0)

        df_tickets = rpt.df_tickets(df_main=_df_by_date)
        if event_type == "Show":
            df_shows: pd.DataFrame = rpt.df_tickets_shows(df_tickets=df_tickets)
            rpt.rpt_tickets_shows(df_shows)

            chart_layout(df_shows,
                         x="show",
                         y=["ticket_sales","ticket_returns"],
                         order_by=["ticket_sales","ticket_returns"],
                         order_by_labels=["sales","returns"])

        if event_type == "Jam":
            df_jams:  pd.DataFrame = rpt.df_tickets_jams(df_tickets=df_tickets)
            rpt.rpt_tickets_jams(df_jams)

            ####
            chart_layout(df_jams,
                         x="jam",
                         y=["ticket_sales","ticket_returns"],
                         order_by=["ticket_sales","ticket_returns"],
                         order_by_labels=["sales","returns"])
            ####



