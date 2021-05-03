import streamlit as st
from missionbio.h5.constants import DNA_ASSAY, PROTEIN_ASSAY
from missionbio.mosaic.constants import NORMALIZED_READS

import defaults as DFT
import interface


def run(sample):
    assay_names = []
    for a in [sample.dna, sample.protein]:
        if a is not None:
            assay_names.append(a.name)

    assay_type, clicked, assay_args = render(sample, assay_names)

    first_pass_preprocess(sample, assay_args)

    if assay_type == DNA_ASSAY:
        preprocess_dna(sample, clicked, *assay_args)
    elif assay_type == PROTEIN_ASSAY:
        preprocess_protein(sample, clicked, *assay_args)

    if clicked:
        interface.rerun()

    available_assays = []
    for a in [sample.dna, sample.protein]:
        if a is not None:
            available_assays.append(a)

            if a.name == assay_type:
                current_assay = a

    interface.subheader(
        f"Analysing {assay_type} | {current_assay.shape[0]} cells | {current_assay.shape[1]} ids | {len(set(current_assay.get_labels()))} clusters"
    )

    return current_assay, available_assays


def render(sample, assay_names):
    with st.sidebar.beta_expander("Preprocessing"):
        info = st.empty()

        assay_name = {DNA_ASSAY: "DNA", PROTEIN_ASSAY: "Protein"}
        assay_type = st.selectbox("Assay", assay_names, format_func=lambda x: assay_name[x])

        if assay_type == DNA_ASSAY:
            dp, gq, af, std = sample.dna.metadata[DFT.PREPROCESS_ARGS]
            dp = st.slider("Minimum read depth (DP)", min_value=0, max_value=100, value=int(dp))
            gq = st.slider(
                "Minimum genotype quality (GQ)", min_value=0, max_value=100, value=int(gq)
            )
            af = st.slider(
                "Minimum allele frequency (VAF)", min_value=0, max_value=100, value=int(af)
            )
            std = st.slider(
                "Minimum standard deviation of AF", min_value=0, max_value=100, value=int(std)
            )
            ids = sample.dna.metadata[DFT.ALL_IDS]
            ids = list(ids[ids.argsort()])
            drop_vars = st.multiselect(
                "Variants to discard", ids, default=sample.dna.metadata[DFT.DROP_IDS]
            )
            keep_vars = st.multiselect(
                "Variants to keep", ids, default=sample.dna.metadata[DFT.KEEP_IDS]
            )

            if len(keep_vars) != 0 and len(drop_vars) != 0:
                interface.error(
                    "Cannot keep and drop variants both. Choose only one of the options"
                )

            assay_args = [drop_vars, keep_vars, dp, gq, af, std]
            n_features = sample.dna.shape[1]

        elif assay_type == PROTEIN_ASSAY:
            ids = sample.protein.metadata[DFT.ALL_IDS]
            ids = list(ids[ids.argsort()])
            drop_abs = st.multiselect(
                "Antibodies to discard", ids, default=sample.protein.metadata[DFT.DROP_IDS]
            )

            assay_args = [drop_abs]
            n_features = sample.protein.shape[1]

        interface.info(f"{assay_type} currently loaded with {n_features} features available", info)

        clicked = st.button("Process")

    return assay_type, clicked, assay_args


def first_pass_preprocess(sample, assay_args):
    for assay in [sample.dna, sample.protein]:
        if assay is not None and assay.metadata[DFT.INITIALIZE]:
            if assay.name == DNA_ASSAY and len(assay_args) == 6:
                preprocess_dna(sample, True, *assay_args)
            elif assay.name == PROTEIN_ASSAY:
                preprocess_protein(sample, True, [])


@st.cache(max_entries=1, hash_funcs=DFT.MOHASH, show_spinner=False)
def preprocess_dna(sample, clicked, drop_vars, keep_vars, dp, gq, af, std):
    args_changed = (
        list(sample.dna.metadata[DFT.PREPROCESS_ARGS]) != [dp, gq, af, std]
        or set(sample.dna.metadata[DFT.DROP_IDS]) != set(drop_vars)
        or set(sample.dna.metadata[DFT.KEEP_IDS]) != set(keep_vars)
    )

    if sample.dna.metadata[DFT.INITIALIZE] or (args_changed and clicked):
        interface.status("Processing DNA assay.")

        sample.reset("dna")

        if len(keep_vars) == 0:
            dna_vars = sample.dna.filter_variants(min_dp=dp, min_gq=gq, min_vaf=af, min_std=std)
            sample.dna.add_metadata(DFT.ALL_IDS, sample.dna.ids())
            if len(drop_vars) > 0:
                sample.dna = sample.dna.drop(drop_vars)
        else:
            dna_vars = keep_vars

        if len(dna_vars) == 0:
            interface.status("Done.")
            interface.error(
                'No variants found. Adjust the filters and process again. Make sure "Filter" is deselected in the Files section.'
            )

        sample.dna = sample.dna[:, dna_vars]
        sample.dna.add_metadata(DFT.PREPROCESS_ARGS, [dp, gq, af, std])
        sample.dna.add_metadata(DFT.DROP_IDS, drop_vars)
        sample.dna.add_metadata(DFT.KEEP_IDS, keep_vars)

        if not sample.dna.metadata[DFT.INITIALIZE]:
            sample.dna.add_metadata(DFT.PREPPED, False)
            sample.dna.add_metadata(DFT.CLUSTERED, False)


@st.cache(max_entries=1, hash_funcs=DFT.MOHASH, show_spinner=False)
def preprocess_protein(sample, clicked, drop_abs):
    if sample.protein.metadata[DFT.INITIALIZE] or (
        set(sample.protein.metadata[DFT.DROP_IDS]) != set(drop_abs) and clicked
    ):
        interface.status("Processing protein assay.")

        sample.reset("protein")

        sample.protein.add_metadata(DFT.ALL_IDS, sample.protein.ids())
        protein = sample.protein.drop(drop_abs) if len(drop_abs) > 0 else sample.protein[:, :]

        for norm in [DFT.CLR, DFT.ASINH, DFT.NSP]:
            protein.normalize_reads(norm)
            protein.add_layer(norm, protein.layers[NORMALIZED_READS])

        sample.protein = protein
        sample.protein.add_metadata(DFT.DROP_IDS, drop_abs)

        if not sample.protein.metadata[DFT.INITIALIZE]:
            sample.protein.add_metadata(DFT.PREPPED, False)
            sample.protein.add_metadata(DFT.CLUSTERED, False)
