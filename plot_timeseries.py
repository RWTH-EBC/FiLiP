"""
This script enables quick visualisation of timeseries data.
It requires streamlit and can be started with:

$ streamlit run plot_timeseries.py

The plot can then be seen on port: 8501

https://towardsdatascience.com/streamlit-101-an-in-depth-introduction-fc8aad9492f2
"""

import streamlit as st
import pandas as pd
import quantum_leap_example as qle

st.title('Plotting Timeseries Data from FiLiP')

st.write("This script enables basic plotting from any pandas.Dataframe object.")
st.write("Currently Line and Box charts are supported.")


@st.cache
def load_data():
    dataframe = qle.create_example_dataframe()
    dataframe = dataframe.set_index("timestamp")
    return dataframe

# Change here to load any data you like from a pandas dataframe
data = load_data()
default_columns = data.columns.tolist()

if st.checkbox("Display the dataframe?", False):
    st.dataframe(data)

cols = st.multiselect("Choose the attributes you would like to display.", data.columns.tolist(), default=default_columns)
option = st.radio("These are the options:", ("None", "Line chart", "Bar chart"))
if option == "None":
    st.write("Please choose an option")
elif option == "Line chart":
    st.line_chart(data[cols])
elif option == "Bar chart":
    st.bar_chart(data[cols])




#ToDo Check how to display categorial data





