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
    """Main function of the App"""
    st.sidebar.title("Navigation")
    selection = st.sidebar.selectbox(
        'Which tutorial would you like to try?',
        list(PAGES.keys()))

    page = PAGES[selection]

    with st.spinner(f"Loading {selection} ..."):
        shared_components.write_page(page)
    st.sidebar.title("INFO  ")
    st.sidebar.info(
        "Python library for easing the handling of the [FiwareAPI](https://fiware-tutorials.readthedocs.io/en/latest/) from python. "
        "INFO 2 ")
    st.sidebar.title("About")
    st.sidebar.info(
        """
        [E.ON Energy Research Center](https://www.ebc.eonerc.rwth-aachen.de/cms/~dmzz/E-ON-ERC-EBC/)
"""
    )


if __name__ == "__main__":
    main()
