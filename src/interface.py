import os
import shutil

import streamlit as st
import defaults as DFT

STATUS = None
ERROR = None
DOWNLOAD = None
SUBHEADER = None


def rerun():
    raise st.script_runner.RerunException(st.script_request_queue.RerunData(None))


def subheader(msg):
    SUBHEADER.subheader(msg)


def info(msg, component=st, color=DFT.BLUE):
    component.markdown(f"<span style='color:{color}'>{msg}</span>", unsafe_allow_html=True)


def error(msg, func=None, render=None):
    global ERROR

    ERROR.markdown(
        f"<p style='font-size:18px'><span style='color:{DFT.RED}'><b>{msg}</b></span></p>",
        unsafe_allow_html=True,
    )

    status("Done.")

    st.stop()


def retry_failed_steps():
    pass


def status(msg):
    global STATUS
    STATUS.markdown(msg, unsafe_allow_html=True)


def download(download_path):
    name = download_path.name
    shutil.rmtree(DFT.DOWNLOADS_PATH)
    os.makedirs(DFT.DOWNLOADS_PATH)
    shutil.copy(download_path, DFT.DOWNLOADS_PATH / name)
    DOWNLOAD.markdown(
        f"<a href='downloads/{name}'>Click here to download {name}</a>", unsafe_allow_html=True
    )


def init():
    global ERROR, DOWNLOAD, SUBHEADER, STATUS

    ERROR = st.empty()
    DOWNLOAD = st.empty()
    SUBHEADER = st.empty()
    STATUS = st.empty()

    hide_streamlit_style = (
        "<style>\n" "#MainMenu {visibility: hidden;}\n" "footer {visibility: hidden;}\n" "</style>"
    )

    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
