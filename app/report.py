"""
All functions in herein assume the joined dataframe produced by transform.get_joined_df()
"""

import pandas as pd
import numpy as np
import streamlit as st

import CONSTANTS as C


@st.cache
def convert_df(df):
    return df.to_csv().encode('utf-8')

#### FILTER FUNTIONS ####

def _df_tickets(df: pd.DataFrame) -> pd.DataFrame:
    df_tickets = df[df["ti_department"] == "Tickets"]
    return df_tickets

def _df_tickets_shows(df: pd.DataFrame) -> pd.DataFrame:
    df_tickets = _df_tickets(df)
    df_shows = df_tickets[df_tickets["ti_category"] == "Show"]
    return df_shows

def _df_tickets_jams(df: pd.DataFrame) -> pd.DataFrame:
    df_tickets = _df_tickets(df)
    df_jams = df_tickets[df_tickets["ti_category"] == "Jam"]
    return df_jams

#### REPORTING FUNTIONS ####
def _ticket_price_by_show(df: pd.DataFrame):
    df = _df_tickets_shows(df)

    report = pd.pivot_table(data=df,
                            index="ti_line_item",
                            aggfunc={"ti_price":np.max})
    report = report.rename(columns={"ti_price":"retail_price"})

    st.dataframe(report.style.set_precision(2))



def _ticket_price_by_jam(df: pd.DataFrame):
    df = _df_tickets_jams(df)
    df["event"] = df["ti_line_item"] + " " + df["date"].astype(str)

    report = pd.pivot_table(data=df,
                            index="event",
                            aggfunc={"ti_price":np.max})
    report = report.rename(columns={"ti_price":"retail_price"})

    st.dataframe(report.style.set_precision(2))


def ticket_price_by_event(df: pd.DataFrame):

    st.header("Ticket Price by Event")
    start = df["date"].min()
    end = df["date"].max()
    st.caption(f"For events between `{start}` and `{end}`")

    radio_event_type = st.radio(label="Select event type",
                                options=["Show","Jam"])

    if radio_event_type == "Show":
        st.subheader("By Show:")
        _ticket_price_by_show(df)

    if radio_event_type == "Jam":
        st.subheader("By Jam:")
        _ticket_price_by_jam(df)
    pass



def ticket_sales_by_jam(df: pd.DataFrame):
    df_tickets = df[df["ti_department"] == "Tickets"]
    df_jams = df_tickets[df_tickets["ti_category"] == "Jam"]

    s_dates: pd.Series = df_jams["t_time"].dt.date
    df_jams["event_title"] = df_jams["ti_line_item"] + " " + s_dates.astype(str)

    report = pd.pivot_table(data=df_jams,
                            index="event_title",
                            aggfunc={
                                "ti_quantity": np.sum,
                                "ti_discounts": np.sum,
                                "ti_total_due": np.sum,
                                "ti_net_total": np.sum
                            })

    st.dataframe(report.style.set_precision(2))


#### WIDGETS ####

def selectbox_event_type():
    st.selectbox(label="Select event type",
                 options=["Show", "Jam"])


if __name__ == '__main__':
    import sys

    _root = r"C:\Users\Alex\PycharmProjects\streamlit_reporting"
    if not _root in sys.path:
        sys.path.insert(0, _root)
    from data.setup_sample import get_sample_joined_df

    joined_df = get_sample_joined_df()
    st.write(joined_df.columns)
