"""Home page shown when the user enters the application"""
import streamlit as st
import os
import filip
import json


CITATIONS =  os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'resources/citations.json')

# pylint: disable=line-too-long
def write():
    """Used to write the page in the app.py file"""
    with st.spinner("Loading Home ..."):

        st.write(
            """
            [FIWARE](hhttps://www.fiware.org/) is an open source platform for accelerating the development of Smart Solutions. 
            The FIWARE Library for Python (FiLiP) offers Python APIs to ease the handling.

            Beside the fact that FIWARE is freely distributed, it comes along with the benefits of a
            large community and offers a set of advanced components including a high performance
            database engine and a sophisticated set of Representational State Transfer (REST) application
            programming interfaces (API) using the standardized Next Generation Service Interface (NGSI)
            format, which is also the formal standard for context information management systems in smart
            cities. Thus, it is promising for future application in BEMS. At the moment, the FIWARE
            catalogue contains about 30 interoperable software modules, so-called Generic Enablers (GE)
            for developing and providing customized IoT platform solutions. This work only employs 
            some core modules of the overall framework in order to proof FIWARE’s general feasibility
            for BAS applications, leaving aside additional GEs, such as the components for user identity
            management.
            
            """)


    st.write("The following papers describe the context in further detail:")

    with open(CITATIONS, 'r') as f:
        data = json.load(f)
        for key, value in data.items():
            st.write(f"[{key}]({value})")


if  __name__ == "__main__":
    write()
