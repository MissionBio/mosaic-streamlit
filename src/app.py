import streamlit as st

import interface
from tasks import load, selection, save

# -------- Sample selection
st.set_page_config(page_title="Mosaic", layout="wide")
interface.init()
interface.subheader("GUI for Mosaic built using Streamlit")
interface.status("v0.4.1")

sample, should_save, save_name = load.run()

# -------- Subsample and assay selection
workflow_steps = selection.run(sample)

# -------- Assay processing
workflow_steps.run()

# -------- Sample save
if should_save:
    save.run(sample, save_name)
