import workflows.general.render as general_render

import interface
import streamlit as st

from const import DNA_LABEL, PROTEIN_LABEL, DENSITY

from missionbio.h5.constants import (
    AF,
    DP,
    GQ,
    NGT,
    SAMPLE
)

from missionbio.mosaic.constants import (
    AF_MISSING,
    NGT_FILTERED,
    PCA_LABEL,
    SCALED_LABEL,
    UMAP_LABEL
)


class Render():
    """
    The function of this class to read the arguments
    from the Argument class and create an appropriate
    GUI for them. It must also provide feedback to the
    Compute class as to whether the step is to be
    processed or not.
    """

    LAYERS = [AF_MISSING, AF, NGT, NGT_FILTERED, GQ, DP]

    def __init__(self, sample, arguments):
        self.sample = sample
        self.arguments = arguments

    def preprocess(self):
        args = self.arguments
        with st.sidebar.beta_expander("Preprocessing"):
            info = st.empty()

            args.dp = st.slider("Minimum read depth (DP)", min_value=0, max_value=100, value=args.get("dp"))
            args.gq = st.slider("Minimum genotype quality (GQ)", min_value=0, max_value=100, value=args.get("gq"))
            args.af = st.slider("Minimum allele frequency (VAF)", min_value=0, max_value=100, value=args.get("af"))
            args.std = st.slider("Minimum standard deviation of AF", min_value=0, max_value=100, value=args.get("std"))

            args.drop_ids = st.multiselect("Variants to discard", args.ids, default=args.get("drop_ids"))
            args.keep_ids = st.multiselect("Variants to keep", args.ids, default=args.get("keep_ids"))

            if len(args.keep_ids) != 0 and len(args.drop_ids) != 0:
                interface.error("Cannot keep and drop variants both. Choose only one of the options")

            interface.info(f"{len(args.ids)} features available", info)

            clicked = st.button("Process")

            return clicked

    def prepare(self):

        args = self.arguments

        with st.sidebar.beta_expander("Data preparation"):
            info = st.empty()

            args.scale_attribute = st.selectbox("Scale - Attribute", self.LAYERS)
            args.pca_attribute = st.selectbox("PCA - Attribute", [SCALED_LABEL] + self.LAYERS)
            args.pca_comps = st.slider("Number of components", 3, 20, args.get("pca_comps"))
            args.umap_attribute = st.selectbox("UMAP - Attribute", [PCA_LABEL, SCALED_LABEL] + self.LAYERS)

            interface.info(
                f"Current transformations are:<br>"
                f"Scale on {args.get('scale_attribute')}<br>"
                f"PCA on {args.get('pca_attribute')}<br>"
                f"UMAP on {args.get('umap_attribute')}",
                info,
            )

            clicked = st.button("Prepare")

        return clicked

    def cluster(self):
        METHODS = ["dbscan", "hdbscan", "graph-community", "kmeans", "count"]

        CLUSTER_OPTIONS = {
            "dbscan": ("Proximity", 0.05, 2.0, 0.2, "eps"),
            "hdbscan": ("Cluster size", 10, 500, 100, "min_cluster_size"),
            "kmeans": ("Neighbours", 2, 30, 5, "n_clusters"),
            "graph-community": ("Neighbours", 10, 500, 100, "k"),
        }

        args = self.arguments

        with st.sidebar.beta_expander("Clustering"):
            info = st.empty()
            args.method = st.selectbox("Method", METHODS, index=2)

            if args.method == "count":
                args.layer = st.selectbox("Layer", [NGT, NGT_FILTERED])
                args.min_clone_size = st.slider("Minimum clone size (%)", 0.0, 10.0, value=args.get("min_clone_size"))
                args.group_missing = st.checkbox("Group missing", args.get("group_missing"))
                args.ignore_zygosity = st.checkbox("Ignore Zygosity", args.get("ignore_zygosity"))
                args.features = st.multiselect("Variants", list(self.sample.dna.ids()), default=args.get("features"))

                description = f"{args.layer} counts on {len(args.features)} variants with {args.min_clone_size}% minimum clone size"
                if args.ignore_zygosity:
                    description += ", ignoring zygosity"
                if args.group_missing:
                    description += ", and grouped missing clones"
                args.cluster_description = description

            else:
                args.attribute = st.selectbox("Attribute", [UMAP_LABEL, PCA_LABEL, AF_MISSING], key="Prepare Attribute", index=2)
                cluster_attr = st.slider(*CLUSTER_OPTIONS[args.method][:-1])
                setattr(args, CLUSTER_OPTIONS[args.method][-1], cluster_attr)
                args.similarity = st.slider("Similarity", 0.0, 1.0, 0.8)

                description = f"{args.method} on {args.attribute} with {CLUSTER_OPTIONS[args.method][0].lower()} "
                description += f"set to {cluster_attr} with {args.similarity} similarity"
                args.cluster_description = description

            interface.info(f"Currently clustered using {args.get('cluster_description')}", info)

            clicked = st.button("Cluster")

        return clicked

    def customize(self):
        general_render.customize(self)

    def layout(self):

        args = self.arguments

        VISUAL_CATEGORY_1 = "Plots"
        VISUAL_CATEGORY_2 = "Tables"

        VISUALS = {
            VISUAL_CATEGORY_1: [
                [2.3, 1, 1.1, 1.45, 1, 1, 1],
                [args.HEATMAP, args.SCATTERPLOT, args.FEATURE_SCATTER, args.VIOLINPLOT, args.RIDGEPLOT, args.STRIPPLOT],
            ],
            VISUAL_CATEGORY_2: [
                [1.65, 1, 1.15, 0.75, 0.75, 1],
                [args.SIGNATURES, args.VAR_ANNOTATIONS, args.COLORS, args.DOWNLOAD],
            ],
        }

        category, kind = args.visual_type
        options = VISUALS[category][1]
        column_sizes = VISUALS[category][0]
        columns = st.beta_columns(column_sizes)
        with columns[0]:
            new_category = st.selectbox("", list(VISUALS.keys()))
            if new_category != category:
                args.visual_type = [new_category, VISUALS[new_category][1][0]]
                interface.rerun()

        for i in range(len(options)):
            with columns[i + 1]:
                clicked = st.button(options[i], key=f"visual-{options[i]}")
                if clicked:
                    kind = options[i]
                    args.visual_type = [category, kind]

        columns = st.beta_columns([0.75, 0.1, 2])
        args.args_container = columns[0]
        args.plot_container = columns[2]

    def visual_arguments(self):

        args = self.arguments
        assay = self.sample.dna

        SPLITBY = [DNA_LABEL, PROTEIN_LABEL, SAMPLE, None]
        COLORBY = [DNA_LABEL, PROTEIN_LABEL, SAMPLE, AF, AF_MISSING, NGT, NGT_FILTERED, GQ, DP, DENSITY, None]

        kind = args.visual_type[1]

        with args.args_container:
            if kind == args.HEATMAP:
                args.attribute_heatmap = st.selectbox("Attribute", self.LAYERS, key="Visualization Attribute")
                args.splitby = st.selectbox("Split by", SPLITBY)
                args.orderby = st.selectbox("Order by", self.LAYERS, key="Visualization Orderby")
                args.cluster_heatmap = st.checkbox("Cluster within labels", True)
                args.convolve = st.slider("Smoothing", 0, 100)
            elif kind == args.SCATTERPLOT:
                args.colorby = st.selectbox("Color by", COLORBY)
                args.features_scatterplot = None
                if args.colorby not in SPLITBY + [DENSITY]:
                    features = st.multiselect("Features", list(assay.ids()), list(assay.ids())[: min(len(assay.ids()), 4)])
                    if len(features) != 0:
                        args.features_scatterplot = features
            elif kind == args.FEATURE_SCATTER:
                pass
            elif kind == args.VIOLINPLOT:
                pass
            elif kind == args.RIDGEPLOT:
                pass
            elif kind == args.STRIPPLOT:
                pass
            elif kind == args.VAR_ANNOTATIONS:
                pass
            elif kind == args.SIGNATURES:
                pass
            elif kind == args.COLORS:
                pass
            elif kind == args.DOWNLOAD:
                pass

    def visual(self):

        args = self.arguments

        with args.plot_container:
            st.plotly_chart(args.fig)
