import numpy as np

import interface
import streamlit as st


def customize(self):

    args = self.arguments

    with st.sidebar.beta_expander("Customizations"):
        interface.info("Rename the labels.<br>Merge by giving the same name.")

        args.label_map = {}
        args.keep_labs = []
        args.palette = self.sample.dna.get_palette()

        lab_set, cnts = np.unique(self.sample.dna.get_labels(), return_counts=True)
        lab_set = lab_set[cnts.argsort()[::-1]]
        for lab in lab_set:
            col1, col2, col3 = st.beta_columns([1, 0.15, 0.1])
            with col1:
                new_name = st.text_input(f"Give a new name to {lab}", lab)
            with col2:
                st.markdown(f"<p style='margin-bottom:34px'></p>", unsafe_allow_html=True)
                args.palette[lab] = st.color_picker("", args.palette[lab], key=f"colorpicker-{lab}")
            with col3:
                st.markdown(f"<p style='margin-bottom:42px'></p>", unsafe_allow_html=True)
                keep = st.checkbox("", True, key=f"keep-cells-{lab}-{lab_set}")
                if keep:
                    args.keep_labs.append(lab)

            if new_name != lab:
                args.label_map[lab] = new_name
                args.palette[new_name] = args.palette[lab]
                del args.palette[lab]

    if len(args.keep_labs) == 0:
        interface.error("At least one label must be selected.")
