from typing import List

import pandas as pd
import streamlit as st
import plotly.express as px
from plotly.graph_objects import Figure

def bar_chart(df,x,y) -> Figure:
    fig = px.bar(df,x=x,y=y)
    return fig

def sbox_bar_chart(figs: List[Figure],
                   options: List[str],
                   sbox_label: str = "Select a chart"):
    sbox = st.selectbox(label=sbox_label,
                        options=[""]+options)

    if sbox in options:
        idx = options.index(sbox)
        fig = figs[idx]

        st.plotly_chart(fig)

def chart_layout(df: pd.DataFrame,
                 x,
                 y,
                 order_by: List[str],
                 order_by_labels: List[str]):

    order_col,chart_col = st.columns([1,4])

    with order_col:

        order_option = st.radio(label="Order By",options=[""]+order_by_labels)
        st.markdown("----")
        order_direction = st.radio(label="",options=["Descending","Ascending"])

        if order_option != "":
            _order_by = order_by[order_by_labels.index(order_option)]

            if order_direction == "Descending":
                _df = df.sort_values(_order_by,ascending=False)
            else:
                _df = df.sort_values(_order_by,ascending=True)

        else:
            _df = df

    with chart_col:

        fig = px.bar(_df,x=x,y=y)
        st.plotly_chart(fig)
