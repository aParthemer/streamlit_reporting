import streamlit as st
import pandas as pd
import numpy as np


st.set_page_config(
     page_title="Ex-stream-ly Cool App",
     page_icon="🧊",
     layout="wide",
     initial_sidebar_state="expanded",
     menu_items={
         'Get Help': 'https://www.extremelycoolapp.com/help',
         'Report a bug': "https://www.extremelycoolapp.com/bug",
         'About': "# This is a header. This is an *extremely* cool app!"
     }
 )

_csv = """
a,b
1,2
3,4
"""

_midi = "/c/Users/Alex/PycharmProjects/MidiCompose/midifiles/kick_side.mid"

with open(_midi,"rb") as f:
    st.write("sick beatz")
    st.download_button("Download MIDI",f,file_name="kick_side.mid",mime="application/octet-stream")

