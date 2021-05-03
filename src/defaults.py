import os
import pathlib

import streamlit as st
from missionbio.h5.constants import AF, DNA_ASSAY, DP, GQ, NGT, PROTEIN_ASSAY
from missionbio.mosaic.constants import (
    AF_MISSING,
    NGT_FILTERED,
    PCA_LABEL,
    SCALED_LABEL,
    UMAP_LABEL,
)
from missionbio.mosaic.dna import Dna as modna
from missionbio.mosaic.protein import Protein as moprotein
from missionbio.mosaic.sample import Sample as mosample

GUI_FRONTEND_RUNNING = os.getenv("MOSAIC_STREAMLIT_GUI_RUNNING", "false") == "true"
MOHASH = {
    moprotein: lambda a: a.name + a.title + str(a.shape),
    modna: lambda a: a.name + a.title + str(a.shape),
    mosample: lambda s: s.name + str(s.dna.shape) + s.load_time,
}


def assay_hash(a):
    palet = ",".join(a.get_palette().keys()) + ",".join(a.get_palette().values())

    hash_val = a.name + str(a.shape) + a.title + palet

    for k in a.row_attrs:
        data = a.row_attrs[k].flatten().astype(str)
        hash_val += ",".join(data)

    return hash_val


def sample_hash(s):
    hash_val = s.name + str(s.dna.shape) + s.load_time

    for a in [s.dna, s.cnv, s.protein]:
        if a is not None:
            hash_val += assay_hash(a)

    return hash_val


MOHASH_COMPLETE = {moprotein: assay_hash, modna: assay_hash, mosample: sample_hash}

ROOT = pathlib.Path(__file__).parent.parent
H5_FOLDER = ROOT / "h5"
if GUI_FRONTEND_RUNNING:
    H5_FOLDER = pathlib.Path.home() / "mosaic-streamlit-h5"
if not H5_FOLDER.is_dir():
    H5_FOLDER.mkdir()

STREAMLIT_STATIC_PATH = pathlib.Path(st.__path__[0]) / "static"
# We create a downloads directory within the streamlit static asset directory
# and we write output files to it
DOWNLOADS_PATH = STREAMLIT_STATIC_PATH / "downloads"
if not DOWNLOADS_PATH.is_dir():
    DOWNLOADS_PATH.mkdir()

# ----------- Interface
RED = "#BF3035"
BLUE = "#1C5C6C"

# ----------- Loading
S3 = "s3"
LOCAL = "local"

# ----------- Preparing
PREPPED = "__mosaic_prepped"

# ----------- Clustering
CLUSTERED = "__mosaic_clustered"
CLUSTER_DESCRIPTION = "__mosaic_cluster_description"

SCALE_ATTR = "__mosaic_data_prep_scale"
PCA_ATTR = "__mosaic_data_prep_pca"
UMAP_ATTR = "__mosaic_data_prep_umap"


CLUSTER_METHOD = {
    DNA_ASSAY: [UMAP_LABEL, "dbscan", 0.2],
    PROTEIN_ASSAY: [PCA_LABEL, "graph-community", 30],
}

CLUSTER_OPTIONS = {
    "dbscan": ("Proximity", 0.05, 2.0, 0.2, "eps"),
    "hdbscan": ("Cluster size", 10, 500, 100, "min_cluster_size"),
    "kmeans": ("Neighbours", 2, 30, 5, "n_clusters"),
    "graph-community": ("Neighbours", 10, 500, 100, "k"),
}

DNA_LABEL = "dna_label"
PROTEIN_LABEL = "protein_label"

CLR = "CLR"
ASINH = "asinh"
NSP = "NSP"
TOTAL_READS = "total_reads"

# ----------- Primary visuals
VISUAL_TYPE = "__mosaic_visual_type"

VISUAL_CATEGORY_1 = "Plots"
VISUAL_CATEGORY_2 = "Tables"
VISUAL_CATEGORY_3 = "Multisample plots"
VISUAL_CATEGORY_4 = "Multiomic plots"

HEATMAP = "Heatmap"
SCATTERPLOT = "Scatterplot"

FEATURE_SCATTER = "Feature Scatter"
VIOLINPLOT = "Violinplot"
RIDGEPLOT = "Ridgeplot"
STRIPPLOT = "Stripplot"

VAR_ANNOTATIONS = "Annotations"
SIGNATURES = "Signatures"
COLORS = "Colors"
DOWNLOAD = "Download"

FISHPLOT = "Fish plot"
BARPLOT = "Bar plot"

DNA_PROTEIN_PLOT = "DNA vs Protein"
DNA_PROTEIN_HEATMAP = "Sample Heatmap"
READ_DEPTH = "Read Depth"

LAYOUT = {
    COLORS: [0.5] + [1] * 10,
}

VISUALS = {
    VISUAL_CATEGORY_1: [
        [2.3, 1, 1.1, 1.45, 1, 1, 1],
        [HEATMAP, SCATTERPLOT, FEATURE_SCATTER, VIOLINPLOT, RIDGEPLOT, STRIPPLOT],
    ],
    VISUAL_CATEGORY_2: [
        [1.65, 1, 1.15, 0.75, 0.75, 1],
        [SIGNATURES, VAR_ANNOTATIONS, COLORS, DOWNLOAD],
    ],
    VISUAL_CATEGORY_3: [[2.43, 0.85, 1, 5], [FISHPLOT, BARPLOT]],
    VISUAL_CATEGORY_4: [
        [1.8, 1.35, 1.25, 1, 1.5],
        [DNA_PROTEIN_HEATMAP, DNA_PROTEIN_PLOT, READ_DEPTH],
    ],
}

# ----------- Visuals options
SPLITBY = {
    DNA_ASSAY: [DNA_LABEL, PROTEIN_LABEL, "sample_name", None],
    PROTEIN_ASSAY: [PROTEIN_LABEL, DNA_LABEL, "sample_name", None],
}
ATTRS_2D = [UMAP_LABEL]
LAYERS = {
    DNA_ASSAY: [AF_MISSING, AF, NGT, NGT_FILTERED, GQ, DP],
    PROTEIN_ASSAY: [CLR, ASINH, NSP, SCALED_LABEL],
}
COLORBY = {
    DNA_ASSAY: [
        DNA_LABEL,
        PROTEIN_LABEL,
        "sample_name",
        AF,
        AF_MISSING,
        NGT,
        NGT_FILTERED,
        GQ,
        DP,
        "density",
        None,
    ],
    PROTEIN_ASSAY: [
        PROTEIN_LABEL,
        DNA_LABEL,
        "sample_name",
        CLR,
        ASINH,
        NSP,
        SCALED_LABEL,
        "density",
        None,
    ],
}

ANNOTATION = "Annotation"
FEATURE_SIGNATURES = "Feature signatures"
ALL_DATA = "All data"
DOWNLOAD_ITEMS = [ANNOTATION, FEATURE_SIGNATURES, ALL_DATA]
