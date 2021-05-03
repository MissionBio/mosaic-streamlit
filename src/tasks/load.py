import os
import time

import missionbio.mosaic.io as mio
import numpy as np
import streamlit as st

import defaults as DFT
import interface


def run():
    file, load_raw, apply_filter, should_save, save_name, info = render()

    if file is None:
        interface.error(
            "Please use the options available in the sidebar to load a sample.<br>"
            f"New h5 files should be copied to the <i>{DFT.H5_FOLDER}/downloads/</i> folder."
        )

    sample = load(file, load_raw, apply_filter)
    interface.info(f"Currently loaded {sample.name}", info)

    return sample, should_save, save_name


def render():
    with st.sidebar.beta_expander("Files", expanded=True):
        info = st.empty()

        if not os.path.exists(DFT.H5_FOLDER / "downloads"):
            os.mkdir(DFT.H5_FOLDER / "downloads/")

        if not os.path.exists(DFT.H5_FOLDER / "analyzed"):
            os.mkdir(DFT.H5_FOLDER / "analyzed/")

        downloaded_files = np.array(os.listdir(DFT.H5_FOLDER / "downloads/"))
        analyzed_files = np.array(os.listdir(DFT.H5_FOLDER / "analyzed/"))
        filenames = list(analyzed_files[analyzed_files.argsort()]) + list(
            downloaded_files[downloaded_files.argsort()]
        )
        filenames = [None] + [f for f in filenames if f[-3:] == ".h5"]

        def shownames(name):
            nonlocal analyzed_files
            if name in analyzed_files:
                return "* " + name
            else:
                return name

        selector = st.empty()
        file = selector.selectbox("Load existing file", filenames, format_func=shownames)

        if file is not None:
            if file in downloaded_files:
                file = DFT.H5_FOLDER / f"downloads/{file}"
            else:
                file = DFT.H5_FOLDER / f"analyzed/{file}"

        col1, col2 = st.beta_columns([0.3, 1])
        with col1:
            # load_raw = st.checkbox("Raw")
            load_raw = False
        with col2:
            # apply_filter = st.checkbox("Filter", False)
            apply_filter = False

        # typed_name = st.text_input("Save, download or delete the given file", value="")
        typed_name = ""

        def _get_file_from_name(typed_name):
            if len(typed_name) == 0:
                interface.error("Please enter a filename")

            if typed_name[-3:] == ".h5":
                typed_name = typed_name[:-3]

            if typed_name + ".h5" in analyzed_files:
                typed_name = DFT.H5_FOLDER / f"analyzed/{typed_name}.h5"
            elif typed_name + ".h5" in downloaded_files:
                typed_name = DFT.H5_FOLDER / f"downloads/{typed_name}.h5"
            else:
                interface.error(f'Cannot find "{typed_name}" in the available files')

            return typed_name

        col1, col2, col3 = st.beta_columns([0.25, 0.4, 0.4])
        with col1:
            st.markdown("")
            # should_save = st.button("Save")
            should_save = False
        with col2:
            st.markdown("")
            # if st.button("Download"):
                # download_path = _get_file_from_name(typed_name)
                # interface.download(download_path)
        with col3:
            st.markdown("")
            # if st.button("Delete"):
            #     typed_name = _get_file_from_name(typed_name)
            #     if file is not None and typed_name == file:
            #         interface.error("Cannot delete the file used in the current analysis.")
            #     os.remove(typed_name)
            #     interface.rerun()

    return file, load_raw, apply_filter, should_save, typed_name, info


@st.cache(max_entries=1, show_spinner=False, allow_output_mutation=True)
def load(path, load_raw, apply_filter):
    interface.status("Reading h5 file.")

    sample = mio.load(path, apply_filter=apply_filter, raw=load_raw)
    sample.load_time = str(time.time())

    if sample.protein is not None:
        try:
            new_ids = np.array([ab.split(" ")[2] for ab in sample.protein.col_attrs["id"]])
        except IndexError:
            new_ids = sample.protein.ids()

        sample.protein.add_col_attr("id", new_ids)
        if sample.protein_raw is not None:
            sample.protein_raw.add_col_attr("id", new_ids)

    return sample


def init_defaults(sample):
    def add_arg(assay, key, val):
        if assay is not None and key not in assay.metadata:
            assay.add_metadata(key, val)

    add_arg(sample.dna, DFT.PREPROCESS_ARGS, [DFT.MIN_DP, DFT.MIN_GQ, DFT.MIN_VAF, DFT.MIN_STD])
    add_arg(sample.dna, DFT.DROP_IDS, [])
    add_arg(sample.dna, DFT.KEEP_IDS, [])
    add_arg(sample.dna, DFT.ALL_IDS, sample.dna.ids())

    if sample.protein is not None:
        add_arg(sample.protein, DFT.DROP_IDS, [])
        add_arg(sample.protein, DFT.ALL_IDS, sample.protein.ids())

    for assay in [sample.dna, sample.protein]:
        add_arg(assay, DFT.VISUAL_TYPE, [DFT.VISUAL_CATEGORY_1, DFT.HEATMAP])
        add_arg(assay, DFT.PREPPED, True)
        add_arg(assay, DFT.CLUSTERED, True)
        add_arg(assay, DFT.INITIALIZE, True)
