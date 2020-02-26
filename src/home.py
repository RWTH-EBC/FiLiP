"""Home page shown when the user enters the application"""
import streamlit as st
import filip


# pylint: disable=line-too-long
def write():
    """Used to write the page in the app.py file"""
    with st.spinner("Loading Home ..."):

        st.write(
            """
[FIWARE](hhttps://www.fiware.org/) is an open source platform for accelerating the development of Smart Solutions. 
The FIWARE Library for Python (FiLiP) offers Python APIs to ease the handling.
            """)


