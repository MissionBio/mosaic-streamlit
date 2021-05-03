import os

import missionbio.mosaic.io as mio

import defaults as DFT
import interface


def run(sample, name):
    interface.status("Saving h5 file.")
    if name == "":
        interface.error("Please provide a name to save by.")
    elif name[-3:] == ".h5":
        name = name[:-3]

    try:
        os.remove(DFT.H5_FOLDER / f"analyzed/{name}.h5")
    except FileNotFoundError:
        pass

    samp = sample[:]
    set_defaults(samp)
    mio.save(samp, DFT.H5_FOLDER / f"analyzed/{name}.h5")

    interface.status("Saved.")
    interface.rerun()


def store_metadata(sample, current_assay, visual_type, available_assays):
    current_assay.add_metadata(DFT.VISUAL_TYPE, visual_type)

    for a in available_assays:
        a.add_metadata(DFT.INITIALIZE, False)

    for assay, og_assay in zip(
        [sample.dna, sample.protein], [sample._original_dna, sample._original_protein]
    ):
        if assay is not None:
            for key in assay.metadata:
                og_assay.add_metadata(key, assay.metadata[key])

            for key in assay.row_attrs:
                og_assay.add_row_attr(key, assay.row_attrs[key])


def set_defaults(sample):
    def del_arg(assay, key):
        if assay is not None:
            assay.del_metadata(key)

    del_arg(sample.dna, DFT.ALL_IDS)
    del_arg(sample.dna, DFT.DROP_IDS)
    del_arg(sample.dna, DFT.KEEP_IDS)

    del_arg(sample.protein, DFT.ALL_IDS)
    del_arg(sample.protein, DFT.DROP_IDS)
