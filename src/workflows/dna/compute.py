import numpy as np
import pandas as pd

import workflows.general.compute as general_compute
import interface

from const import DNA_LABEL, ASSAY_LABELS

from missionbio.mosaic.constants import AF_MISSING, UMAP_LABEL


class Compute():

    def __init__(self, sample, arguments):
        self._original_sample = sample
        self.sample = sample
        self.arguments = arguments

    def preprocess(self):
        args = self.arguments
        interface.status("Processing DNA assay.")

        self.sample.reset("dna")

        if len(args.keep_ids) == 0:
            dna_vars = self.sample.dna.filter_variants(min_dp=args.dp, min_gq=args.gq, min_vaf=args.af, min_std=args.std)
            if len(args.drop_ids) > 0:
                dna_vars = list(set(dna_vars) - set(args.drop_ids))
        else:
            dna_vars = args.keep_ids

        if len(dna_vars) == 0:
            interface.error("No variants found. Adjust the filters and process again.")

        self.sample.dna = self.sample.dna[:, dna_vars]

    def prepare(self):
        args = self.arguments
        assay = self.sample.dna

        interface.status(f'Preparing DNA variants data.')

        assay.scale_data(args.scale_attribute)
        assay.run_pca(args.pca_attribute, components=args.pca_comps)
        assay.run_umap(attribute=args.umap_attribute, random_state=42)

    def cluster(self):
        args = self.arguments
        assay = self.sample.dna

        interface.status(f'Clustering DNA variants data.')

        kwargs = {
            "dbscan": {"eps": args.eps},
            "hdbscan": {"min_cluster_size": args.min_cluster_size},
            "graph-community": {"k": args.k},
            "kmeans": {"n_clusters": args.n_clusters}
        }

        if args.method in ["dbscan", "hdbscan", "graph-community", "kmeans"]:
            assay.cluster(method=args.method, attribute=args.attribute, **kwargs[args.method])
            assay.cluster_cleanup(AF_MISSING, args.similarity)
        elif args.method == "count":
            df = assay.count(layer=args.layer,
                             min_clone_size=args.min_clone_size,
                             group_missing=args.group_missing,
                             ignore_zygosity=args.ignore_zygosity,
                             features=args.features)

            if df is not None:
                lab_map = {}
                for clone in df.index:
                    score = df.loc[clone, "score"]
                    if score > 0:
                        new_name = f"{clone} ({score:.2f})"
                        lab_map[str(clone)] = new_name
                assay.rename_labels(lab_map)

        general_compute.add_label(self.sample, assay, DNA_LABEL)

    def customize(self):
        general_compute.customize(self)

    def visual(self):

        args = self.arguments
        assay = self.sample.dna

        kind = args.visual_type[1]

        interface.status(f'Creating {kind}.')

        if kind == args.HEATMAP:
            if args.splitby in ASSAY_LABELS:
                general_compute.set_label(self.sample, assay, args.splitby)
                args.splitby = "label"

            bo = assay.clustered_barcodes(orderby=args.orderby, splitby=args.splitby)
            if not args.cluster_heatmap:
                labels = assay.get_labels()[[np.where(assay.barcodes() == b)[0][0] for b in bo]]
                bo = []
                for lab in pd.unique(labels):
                    bo.extend(assay.barcodes(lab))
                bo = np.array(bo)

            feats = assay.clustered_ids(orderby=args.orderby)
            args.fig = assay.heatmap(attribute=args.attribute_heatmap, bars_order=bo, features=feats, convolve=args.convolve, splitby=args.splitby)
            general_compute.set_label(self.sample, assay, DNA_LABEL)

        elif kind == args.SCATTERPLOT:
            if UMAP_LABEL not in assay.row_attrs:
                interface.error("UMAP has not been run yet. Run it under the Data Preparation step.")

            if args.colorby in ASSAY_LABELS:
                general_compute.set_label(self.sample, assay, args.colorby)
                args.colorby = "label"

            args.fig = assay.scatterplot(attribute=UMAP_LABEL, colorby=args.colorby, features=args.features_scatterplot)
            general_compute.set_label(self.sample, assay, DNA_LABEL)

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
