"""
This script enables quick visualisation of various scripts explaining filip.
It requires streamlit and can be started with:

$ streamlit run app.py

The plot can then be seen on port: 8501

https://towardsdatascience.com/streamlit-101-an-in-depth-introduction-fc8aad9492f2
"""

from src import shared_components, plot_timeseries, home, cb_tutorial, ts_tutorial, iot_tutorial, sub_tutorial
import streamlit as st


PAGES = {
    "Home" : home,
    "Plotting" : plot_timeseries,
    "Context Broker Tutorial": cb_tutorial,
    "Quantum Leap Tutorial": ts_tutorial,
    "Subscription Tutorial": sub_tutorial,
    "IOT Tutorial": iot_tutorial

}


def main():
    """Main function of the App.
    Is is used to enable the selection of the other pages / functions"""
    st.sidebar.title("Navigation")
    selection = st.sidebar.selectbox(
        'Which tutorial would you like to try?',
        list(PAGES.keys()))

    page = PAGES[selection]

    st.sidebar.title("INFO")
    st.sidebar.info(
        "[FIWARE](hhttps://www.fiware.org/) is an open source platform for accelerating the development of Smart Solutions. "
        "The FIWARE Library for Python (FiLiP) offers Python APIs to ease the handling of the [FiwareAPI](https://fiware-tutorials.readthedocs.io/en/latest/).")
    st.sidebar.title("About")
    st.sidebar.info(
        """
        [E.ON Energy Research Center](https://www.ebc.eonerc.rwth-aachen.de/cms/~dmzz/E-ON-ERC-EBC/)
"""
    )
    st.sidebar.image("resources/ERC_RWTH_LOGO.png", use_column_width=True)

    with st.spinner(f"Loading {selection} ..."):
        shared_components.write_page(page)




if __name__ == "__main__":
    main()
