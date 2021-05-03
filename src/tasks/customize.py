import numpy as np
import streamlit as st

import defaults as DFT
import interface


def run(sample, assay):
    lab_map, pal, keep_labs = render(assay)

    customize_labels(assay, lab_map, pal)

    sample_kept, assay_kept = filter_sample(sample, assay, keep_labs)

    return sample_kept, assay_kept


def render(assay):
    with st.sidebar.beta_expander("Customizations"):
        interface.info("Rename the labels.<br>Merge by giving the same name.")

        lab_map = {}
        keep_labs = []
        pal = assay.get_palette()

        lab_set = np.unique(assay.get_labels())
        for lab in lab_set:
            col1, col2, col3 = st.beta_columns([1, 0.15, 0.1])
            with col1:
                new_name = st.text_input(f"Give a new name to {lab}", lab)
            with col2:
                st.markdown(f"<p style='margin-bottom:34px'></p>", unsafe_allow_html=True)
                pal[lab] = st.color_picker("", pal[lab], key=f"colorpicker-{lab}")
            with col3:
                st.markdown(f"<p style='margin-bottom:42px'></p>", unsafe_allow_html=True)
                keep = st.checkbox("", True, key=f"keep-cells-{lab}-{lab_set}")
                if keep:
                    keep_labs.append(lab)

            if new_name != lab:
                lab_map[lab] = new_name
                pal[new_name] = pal[lab]
                del pal[lab]

    if len(keep_labs) == 0:
        interface.error("At least one label must be selected.")

    return lab_map, pal, keep_labs


@st.cache(max_entries=1, hash_funcs=DFT.MOHASH, show_spinner=False)
def customize_labels(assay, lab_map, pal):
    old_labs = set(assay.get_labels())
    old_pal = assay.get_palette()
    assay.rename_labels(lab_map)
    assay.set_palette(pal)
    new_labs = set(assay.get_labels())

    if new_labs != old_labs or old_pal != pal:
        interface.rerun()


@st.cache(
    max_entries=1, hash_funcs=DFT.MOHASH_COMPLETE, show_spinner=False, allow_output_mutation=True
)
def filter_sample(sample, assay, keep_labs):
    assay_kept = assay[assay.barcodes(keep_labs), :]
    sample_kept = sample[assay.barcodes(keep_labs)]

    return sample_kept, assay_kept
