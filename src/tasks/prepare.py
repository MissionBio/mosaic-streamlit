import streamlit as st
from missionbio.h5.constants import DNA_ASSAY, PROTEIN_ASSAY
from missionbio.mosaic.constants import AF_MISSING, PCA_LABEL, SCALED_LABEL, UMAP_LABEL

import defaults as DFT
import interface


def run(assay, available_assays):
    clicked, scale_attribute, pca_attribute, umap_attribute, pca_comps, info = render(assay)

    first_pass_prepare(available_assays)

    if clicked:
        prepare(assay, scale_attribute, pca_attribute, umap_attribute, pca_comps)
        interface.rerun()

    interface.info(
        f"Current transformations are:<br>"
        f"Scale on {assay.metadata[DFT.SCALE_ATTR]}<br>"
        f"PCA on {assay.metadata[DFT.PCA_ATTR]}<br>"
        f"UMAP on {assay.metadata[DFT.UMAP_ATTR]}",
        info,
    )


def render(assay):
    title = "Data preparation"
    if not assay.metadata[DFT.PREPPED]:
        title += " *"

    with st.sidebar.beta_expander(title):
        info = st.empty()

        scale_attribute = st.selectbox("Scale - Attribute", DFT.LAYERS[assay.name])
        pca_attribute = st.selectbox("PCA - Attribute", ["scaled_counts"] + DFT.LAYERS[assay.name])

        pca_comps = 6
        pca_comps = st.slider("Number of components", 3, 20, 6)

        umap_attribute = st.selectbox(
            "UMAP - Attribute", ["pca", "scaled_counts"] + DFT.LAYERS[assay.name]
        )

        clicked = st.button("Prepare")

    return clicked, scale_attribute, pca_attribute, umap_attribute, pca_comps, info


def first_pass_prepare(available_assays):
    for prep_assay in available_assays:
        if prep_assay.metadata[DFT.INITIALIZE]:
            if prep_assay.name == DNA_ASSAY:
                prepare(
                    prep_assay, AF_MISSING, SCALED_LABEL, AF_MISSING, min(len(prep_assay.ids()), 8)
                )
            elif prep_assay.name == PROTEIN_ASSAY:
                prepare(
                    prep_assay,
                    DFT.LAYERS[prep_assay.name][0],
                    SCALED_LABEL,
                    PCA_LABEL,
                    min(len(prep_assay.ids()), 8),
                )


@st.cache(max_entries=1, hash_funcs=DFT.MOHASH, show_spinner=False)
def prepare(assay, scale_attribute, pca_attribute, umap_attribute, pca_comps):
    interface.status(f'Preparing {assay.name.replace("_", " ")} data.')

    attr = scale_attribute
    if (
        SCALED_LABEL not in assay.layers
        or assay.metadata[DFT.SCALE_ATTR] != attr
        or not assay.metadata[DFT.PREPPED]
    ):
        assay.scale_data(scale_attribute)
        assay.add_metadata(DFT.SCALE_ATTR, attr)

    attr = f"{pca_attribute}"
    if pca_attribute == SCALED_LABEL:
        attr = f"scaled {scale_attribute}"

    if (
        PCA_LABEL not in assay.row_attrs
        or assay.metadata[DFT.PCA_ATTR] != attr
        or not assay.metadata[DFT.PREPPED]
    ):
        assay.run_pca(pca_attribute, components=pca_comps)
        assay.add_metadata(DFT.PCA_ATTR, attr)

    attr = f"{umap_attribute}"
    if umap_attribute == SCALED_LABEL:
        attr = f"scaled {scale_attribute}"
    if umap_attribute == PCA_LABEL:
        if pca_attribute == SCALED_LABEL:
            attr = f"PCA of scaled {scale_attribute}"
        else:
            attr = f"PCA of {pca_attribute}"

    if (
        UMAP_LABEL not in assay.row_attrs
        or assay.metadata[DFT.UMAP_ATTR] != attr
        or not assay.metadata[DFT.PREPPED]
    ):
        assay.run_umap(attribute=umap_attribute, random_state=42)
        assay.add_metadata(DFT.UMAP_ATTR, attr)

    if not assay.metadata[DFT.INITIALIZE]:
        assay.add_metadata(DFT.CLUSTERED, False)

    assay.add_metadata(DFT.PREPPED, True)
