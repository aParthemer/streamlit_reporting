"""
All functions in herein assume the joined dataframe produced by transform.get_joined_df()
"""
from typing import List

import pandas as pd
import numpy as np
import streamlit as st
from pandasql import sqldf

import CONSTANTS as C


@st.cache
def df_to_csv(df: pd.DataFrame,
              encoding: str = 'utf-8'):
    return df.to_csv().encode(encoding)


#### FILTER FUNTIONS ####

@st.cache
def df_tickets(df_main: pd.DataFrame) -> pd.DataFrame:
    q_tickets = \
        """
    SELECT `ti_line_item`,`ti_operation_type`,`ti_category`,`ti_price`,`ti_quantity`,
            `ti_modifiers`,`ti_discounts`,`ti_net_total`,`t_time`
    FROM df_main
    WHERE 
        `ti_department` = "Tickets"
    """
    df_tickets: pd.DataFrame = sqldf(q_tickets, locals())

    return df_tickets


@st.cache
def df_tickets_shows(df_tickets: pd.DataFrame) -> pd.DataFrame:
    q_tickets_shows = \
        """
    SELECT 
        `ti_line_item` AS `show`,
        SUM(CASE
            WHEN `ti_operation_type` = 'SALE' THEN `ti_quantity`
            ELSE 0
            END) AS `ticket_sales`,
        SUM(CASE
            WHEN `ti_operation_type` = 'RETURN' THEN `ti_quantity`
            ELSE 0
            END) as `ticket_returns`,
        MAX(`ti_price`) as `price`,
        SUM(`ti_modifiers`) as `modifiers`,
        SUM(`ti_discounts`) as `discounts`,
        SUM(`ti_net_total`) as `net_total`
    FROM df_tickets   
    WHERE `ti_category` = 'Show'
    GROUP BY `ti_line_item`
    """
    df_show_sales: pd.DataFrame = sqldf(q_tickets_shows, locals())

    return df_show_sales


@st.cache
def df_tickets_jams(df_tickets: pd.DataFrame) -> pd.DataFrame:
    q_tickets_jams = \
        """
    SELECT 
        `ti_line_item` || " - " || DATE(`t_time`) AS `jam`,
        SUM(CASE
            WHEN `ti_operation_type` = 'SALE' THEN `ti_quantity`
            ELSE 0
            END) AS `ticket_sales`,
        SUM(CASE
            WHEN `ti_operation_type` = 'RETURN' THEN `ti_quantity`
            ELSE 0
            END) as `ticket_returns`,
        SUM(`ti_modifiers`) as `modifiers`,
        SUM(`ti_discounts`) as `discounts`,
        SUM(`ti_net_total`) as `net_total`
    FROM df_tickets   
    WHERE `ti_category` = 'Jam'
    GROUP BY `jam`
    """
    df_jam_sales: pd.DataFrame = sqldf(q_tickets_jams, locals())

    return df_jam_sales


#### REPORTING FUNCTIONS ####

def rpt_tickets_shows(df_tickets_shows: pd.DataFrame):
    st.markdown("""
    ----
    #### By Show
    
    > **note** :
    
    > > Some shows have multiple prices listed in the transaction records. In the table below,
    the "price" column reflects the *maximum* price of the prices listed for a particular show,
    on the assumption that the maximum price best reflects the "retail" price of a ticket. 
    
    ----
    """)

    col_filters,col_data = st.columns([1,4])
    with col_filters:
        sbox = st.selectbox("Order by (greatest to least)",
                            options=["",
                                     "ticket_sales",
                                     "ticket_returns",
                                     "net_total"]
                            )
        if sbox == "ticket_sales":
            _df = df_tickets_shows.sort_values("ticket_sales",ascending=False)
        elif sbox == "ticket_returns":
            _df = df_tickets_shows.sort_values("ticket_returns", ascending=False)
        elif sbox == "net_total":
            _df = df_tickets_shows.sort_values("net_total", ascending=False)
        else:
            _df = df_tickets_shows

    with col_data:
        st.dataframe(_df.style.set_precision(2))
        btn_download_csv(_df,
                         file_name="ticket_sales_by_show.csv")


def rpt_tickets_jams(df_tickets_jams: pd.DataFrame):
    st.markdown(
        """
    ----
    #### By Jam
    
    > **note** : 
    
    > > Currently jams are not being given distinctive titles in shopkeep,
    so the date next to each jam doesn't necessarily reflect a distinct "event",
    but rather the date of the transaction. (ie. There was no Pro Jam on 12-13-2021 (a Monday), but there were apparently tickets bought and returned on that day
    pertaining to a "Pro Jam" line item.)
    > > 
    > > We might address this in the future by enforcing some stronger naming conventions in ShopKeep,
    but for now this serves as a close approximation of "per jam" granularity.
    
    ----
""")
    col_filters, col_data = st.columns([1, 4])
    with col_filters:
        sbox = st.selectbox("Order by (greatest to least)",
                            options=["",
                                     "ticket_sales",
                                     "ticket_returns",
                                     "net_total"]
                            )
        if sbox == "ticket_sales":
            _df = df_tickets_jams.sort_values("ticket_sales",ascending=False)
        elif sbox == "ticket_returns":
            _df = df_tickets_jams.sort_values("ticket_returns",ascending=False)
        elif sbox == "net_total":
            _df = df_tickets_jams.sort_values("net_total",ascending=False)
        else:
            _df = df_tickets_jams

    with col_data:
        st.dataframe(_df.style.set_precision(2))
        btn_download_csv(_df,
                         file_name="ticket_sales_by_jam.csv")




#### WIDGETS ####

def selectbox_event_type():
    st.selectbox(label="Select event type",
                 options=["Show", "Jam"])


def btn_download_csv(df: pd.DataFrame,
                     file_name: str,
                     label="Download CSV",
                     encoding="utf-8"):
    csv = df_to_csv(df=df,
                    encoding=encoding)
    btn = st.download_button(label=label,
                             data=csv,
                             file_name=file_name,
                             mime='text/csv')
    return btn


def exp_download_multi_csv(dfs: List[pd.DataFrame],
                           file_names: List[str],
                           labels: List[str],
                           exp_label: str = "Download CSV",
                           encoding: str = "utf-8"):
    csvs = [df_to_csv(df=df, encoding=encoding) for df in dfs]
    with st.expander(label=exp_label):
        for csv, label, fname in zip(csvs, labels, file_names):
            st.download_button(label=label,
                               data=csv,
                               file_name=fname,
                               mime="text/csv")

