import numpy as np
import streamlit as st
from missionbio.h5.constants import DNA_ASSAY, PROTEIN_ASSAY
from missionbio.mosaic.constants import AF_MISSING, PCA_LABEL, UMAP_LABEL

import defaults as DFT
import interface


def run(assay, available_assays):
    clicked, method, description, cluster_kwargs, info = render(assay)

    first_pass_cluster(available_assays)

    if clicked:
        cluster(assay, method, description, **cluster_kwargs)
        interface.rerun()
    interface.info(f"Currently clustered using {assay.metadata[DFT.CLUSTER_DESCRIPTION]}", info)


def render(assay):
    title = "Clustering"
    if not assay.metadata[DFT.CLUSTERED]:
        title += " *"

    with st.sidebar.beta_expander(title):
        info = st.empty()

        all_methods = ["dbscan", "hdbscan", "graph-community", "kmeans"]
        if assay.name == DNA_ASSAY:
            all_methods.append("count")
        elif assay.name == PROTEIN_ASSAY:
            all_methods.append("gating")
        method = st.selectbox("Method", all_methods)

        cluster_kwargs = {}
        if method == "count":
            layer = st.selectbox("Layer", ["NGT", "NGT_FILTERED"])
            min_clone_size = st.slider("Minimum clone size (%)", 0.0, 10.0, 1.0)
            group_missing = st.checkbox("Group missing", True)
            ignore_zygosity = st.checkbox("Ignore Zygosity", False)
            features = st.multiselect("Variants", list(assay.ids()))

            description = f"{layer} counts on {len(features)} variants with {min_clone_size}% minimum clone size"
            if ignore_zygosity:
                description += ", ignoring zygosity"
            if group_missing:
                description += ", and grouped missing clones"

            cluster_kwargs = {
                "assay_to_count": assay,
                "features": features,
                "layer": layer,
                "group_missing": group_missing,
                "min_clone_size": min_clone_size,
                "ignore_zygosity": ignore_zygosity,
            }

            method = count_dna

        elif method == "gating":
            layer = st.selectbox("Layer", [DFT.CLR, DFT.NSP, DFT.ASINH])
            data = assay.get_attribute(layer, constraint="row+col")
            columns = st.beta_columns([0.55, 0.75])
            with columns[0]:
                feature_x = st.selectbox("Feature x", list(assay.ids()), index=0)
                feature_y = st.selectbox("Feature y", list(assay.ids()), index=1)
            with columns[1]:
                vals = data[feature_x].values
                threshold_x = st.number_input(
                    "X threshold", float(min(vals)), float(max(vals)), float(vals.mean()), step=None
                )
                vals = data[feature_y].values
                threshold_y = st.number_input(
                    "Y Threshold", float(min(vals)), float(max(vals)), float(vals.mean()), step=None
                )

            fig = get_gating_plot(assay, layer, feature_x, feature_y, threshold_x, threshold_y)
            st.plotly_chart(fig)

            description = f"gating on {layer}, with {feature_x} ({threshold_x:.2f}) and {feature_y} ({threshold_y:.2f})"

            cluster_kwargs = {
                "assay_to_gate": assay,
                "features": [feature_x, feature_y],
                "thresholds": [threshold_x, threshold_y],
                "layer": layer,
            }

            method = gate_protein

        else:
            attribute = st.selectbox("Attribute", [UMAP_LABEL, PCA_LABEL], key="Prepare Attribute")
            cluster_arg = st.slider(*DFT.CLUSTER_OPTIONS[method][:-1])

            description = f"{method} on {attribute} with {DFT.CLUSTER_OPTIONS[method][0].lower()} set to {cluster_arg}"
            cluster_kwargs = {
                "attribute": attribute,
                "method": method,
                DFT.CLUSTER_OPTIONS[method][-1]: cluster_arg,
            }

            if assay.name == DNA_ASSAY:
                cluster_kwargs["similarity"] = st.slider("Similarity", 0.0, 1.0, 0.8)
                description = description + f" with {cluster_kwargs['similarity']} similarity"

            method = assay.cluster

        clicked = st.button("Cluster")

    return clicked, method, description, cluster_kwargs, info


def first_pass_cluster(available_assays):
    for prep_assay in available_assays:
        if prep_assay.metadata[DFT.INITIALIZE]:
            attribute, method, cluster_arg = DFT.CLUSTER_METHOD[prep_assay.name]
            description = f"{method} on {attribute} with {DFT.CLUSTER_OPTIONS[method][0]} set to {cluster_arg}"
            cluster_kwargs = {
                "attribute": attribute,
                "method": method,
                DFT.CLUSTER_OPTIONS[method][-1]: cluster_arg,
            }
            if prep_assay.name == DNA_ASSAY:
                cluster_kwargs["similarity"] = 0.8
                description = description + f" with {cluster_kwargs['similarity']} similarity"
            cluster(prep_assay, prep_assay.cluster, description, **cluster_kwargs)


@st.cache(max_entries=1, hash_funcs=DFT.MOHASH, show_spinner=False)
def get_gating_plot(assay, layer, feature_x, feature_y, threshold_x, threshold_y):
    fig = assay.feature_scatter(layer=layer, ids=[feature_x, feature_y], colorby="density")
    fig.add_hline(y=threshold_y, line_width=2)
    fig.add_vline(x=threshold_x, line_width=2)
    fig.update_layout(
        coloraxis_showscale=False,
        title="",
        height=275,
        width=275,
        xaxis_fixedrange=True,
        yaxis_fixedrange=True,
        xaxis_title_font_size=10,
        yaxis_title_font_size=10,
        margin=dict(l=0, r=1, b=1, t=1),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_traces(hovertemplate="%{x:.2f}, %{y:.2f}<extra></extra>")

    return fig


def gate_protein(assay_to_gate, layer, features, thresholds):
    data = assay_to_gate.get_attribute(layer, constraint="row+col")
    data = data[features]
    lab_map = {}
    bars = data.index.values
    lab_map[f"{features[0]}+ & {features[1]}+"] = bars[
        np.logical_and(data[features[0]] > thresholds[0], data[features[1]] > thresholds[1])
    ]
    lab_map[f"{features[0]}+ & {features[1]}-"] = bars[
        np.logical_and(data[features[0]] > thresholds[0], data[features[1]] < thresholds[1])
    ]
    lab_map[f"{features[0]}- & {features[1]}+"] = bars[
        np.logical_and(data[features[0]] < thresholds[0], data[features[1]] > thresholds[1])
    ]
    lab_map[f"{features[0]}- & {features[1]}-"] = bars[
        np.logical_and(data[features[0]] < thresholds[0], data[features[1]] < thresholds[1])
    ]

    assay_to_gate.set_labels(lab_map)


def count_dna(assay_to_count, features, layer, group_missing, min_clone_size, ignore_zygosity):
    df = assay_to_count.count(
        features=features,
        layer=layer,
        group_missing=group_missing,
        min_clone_size=min_clone_size,
        ignore_zygosity=ignore_zygosity,
    )

    if df is not None:
        lab_map = {}
        for clone in df.index:
            score = df.loc[clone, "score"]
            if score > 0:
                new_name = f"{clone} ({score:.2f})"
                lab_map[str(clone)] = new_name
        assay_to_count.rename_labels(lab_map)


@st.cache(max_entries=1, hash_funcs=DFT.MOHASH, show_spinner=False)
def cluster(assay, method_func, description, **kwargs):
    similarity = None
    if "similarity" in kwargs:
        similarity = kwargs["similarity"]
        del kwargs["similarity"]

    if (
        DFT.CLUSTER_DESCRIPTION not in assay.metadata
        or assay.metadata[DFT.CLUSTER_DESCRIPTION] != description
        or not assay.metadata[DFT.CLUSTERED]
    ):
        interface.status(f'Clustering {assay.name.replace("_", " ")}')
        method_func(**kwargs)
        if similarity is not None:
            assay.cluster_cleanup(AF_MISSING, similarity)

        assay.add_metadata(DFT.CLUSTER_DESCRIPTION, description)

    assay.add_metadata(DFT.CLUSTERED, True)
