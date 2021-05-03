import streamlit as st
import importlib

import interface

from missionbio.mosaic.sample import Sample as mosample


"""
The key is the name of the attribute in the
sample object and the value is the name that
is to be displayed in the app.
"""
AVAILABLE_WORKFLOWS = {
    "dna": "DNA",
    # "protein": "Protein",
    # "cnv": "CNV"
}

SAMPLE_HASH = {mosample: lambda s: s.name + s.load_time}


def run(sample):
    selected_assay = render(sample)

    assay = getattr(sample, selected_assay)
    interface.subheader(
        f"Analysing {selected_assay} | {assay.shape[0]} cells | {assay.shape[1]} ids | {len(set(assay.get_labels()))} clusters"
    )

    steps = initialize_steps(sample)
    selected_steps = steps[selected_assay]

    return selected_steps


def render(sample):
    with st.sidebar:
        all_assays = list(AVAILABLE_WORKFLOWS.keys())
        selected_assay = st.selectbox("Workflow", all_assays, format_func=lambda x: AVAILABLE_WORKFLOWS[x])

    return selected_assay


@st.cache(max_entries=1, show_spinner=False, hash_funcs=SAMPLE_HASH, allow_output_mutation=True)
def initialize_steps(sample):
    steps = {}

    for a in AVAILABLE_WORKFLOWS:
        theclass = getattr(importlib.import_module(f"workflows.{a}.steps"), "Steps")
        steps[a] = theclass(sample)

    return steps
