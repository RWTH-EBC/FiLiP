"""Components for the Awesome Streamlit App and other use cases
Hopefully a lot of the components  will be removed again as the streamlit api is extended"""
import base64
import importlib
import logging
import sys
from typing import Any, List
import inspect
import streamlit as st
import json

logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)


def _reload_module(page):
    """Reloads the specified module/ page
    Arguments:
        page {module} -- A page/ module
    """
    logging.debug(
        """--- Reload of module for live reload to work on deeply imported python modules.
    Cf. https://github.com/streamlit/streamlit/issues/366 ---"""
    )
    logging.debug("2. Module: %s", page)
    logging.debug("3. In sys.modules: %s", page in sys.modules)
    try:
        importlib.import_module(page.__name__)
        importlib.reload(page)
    except ImportError as _:
        logging.debug("4. Writing: %s", page)
        logging.debug("5. In sys.modules: %s", page in sys.modules)


def write_page(page):  # pylint: disable=redefined-outer-name
    """Writes the specified page/module
    Our multipage app is structured into sub-files with a `def write()` function
    Arguments:
        page {module} -- A module with a 'def write():' function
    """
    # _reload_module(page)
    page.write()


def display_code(func):
    """Displays the specificied function
    Our tutorial is structured into a variety of helper functions. These can be displayed applying the display_code function
    :param func - A Function where the source code should be displayed
    """
    fun_code = inspect.getsource(func)
    st.code(fun_code)


def pretty_print_json(data):
    """
    Function pretty prints a JSON-
    :param data - A string, containting data in the dictionary schema
    :return a streamlit pretty printed json
    """
    if isinstance(data, dict):
        data = json.dumps(data)
    json_data = json.loads(data)
    st.json(json_data)

def video_youtube(src: str, width="100%", height=315):
    """An extension of the video widget
    Arguments:
        src {str} -- A youtube url like https://www.youtube.com/embed/B2iAodr0fOo
    Keyword Arguments:
        width {str} -- The width of the video (default: {"100%"})
        height {int} -- The height of the video (default: {315})
    """
    st.write(
        f'<iframe width="{width}" height="{height}" src="{src}" frameborder="0" '
        'allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" '
        "allowfullscreen></iframe>",
        unsafe_allow_html=True,
    )


def multiselect(label: str, options: List[Any], default: List[Any], format_func=str) -> List[Any]:
    """multiselect extension that enables default to be a subset list of the list of objects
     - not a list of strings.
     Assumes that options have unique format_func representations
     cf. https://github.com/streamlit/streamlit/issues/352
    Arguments:
        label {str} -- A label to display above the multiselect
        options {List[Any]} -- A list of objects
        default {List[Any]} -- A list of objects to be selected by default
    Keyword Arguments:
        format_func {[type]} -- [description] (default: {str})
    Returns:
        [type] -- [description]
    """

    options_ = {format_func(option): option for option in options}
    default_ = [format_func(option) for option in default]
    selections = st.multiselect(
        label, options=list(options_.keys()), default=default_, format_func=format_func
    )
    return [options_[format_func(selection)] for selection in selections]


# ToDo Write default none selection so if needed user input does not automatically selects something

def default_selection(options:list):
    default_option = [""]
    return default_option.extend(options)


def title_EBC():

    """Uses st.write to write the title as f'Awesome Streamlit {body}'
    - plus the awesome badge
    - plus a link to the awesome-streamlit GitHub page
    Arguments:
        body {str} -- [description]
    """
    path_to_logo = "resources/ERC_RWTH_LOGO.png"
    return st.image(path_to_logo, caption='Welcome to the FIWARE Library for Python.',
                    use_column_width=False)


def write_svg(svg: str):
    """Renders the given svg string.
    Arguments:
        svg {str} -- A string containing svgs
    """
    b64 = base64.b64encode(svg.encode("utf-8")).decode("utf-8")
    html = r'<img src="data:image/svg+xml;base64,%s"/>' % b64
    st.write(html, unsafe_allow_html=True)

def multiselect(label, options, default, format_func=str):
    """multiselect extension that enables default to be a subset list of the list of objects
     - not a list of strings

     Assumes that options have unique format_func representations

     cf. https://github.com/streamlit/streamlit/issues/352
     """
    options_ = {format_func(option): option for option in options}
    default_ = [format_func(option) for option in default]
    selections = st.multiselect(
        label, options=list(options_.keys()), default=default_, format_func=format_func
    )
    return [options_[format_func(selection)] for selection in selections]


def horizontal_ruler(in_sidebar: bool = False):
    """Inserts a horizontal ruler (like <hr> in HTML)
    Keyword Arguments:
        in_sidebar {bool} -- If True the ruler is inserted in the sidebar (default: {False})
    """
    if in_sidebar:
        return st.sidebar.markdown("---")

    return st.markdown("---")


def timeseries_to_df(dataframe):
    """"
    Helper Function to turn a timeseries into a dataframe.
    """
    # ToDo put from TS-tutorial here
    pass

