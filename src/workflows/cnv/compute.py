import numpy as np
import pandas as pd

import interface


class Compute():

    def __init__(self, sample, arguments):
        self.sample = sample
        self.arguments = arguments

    def preprocess(self):
        interface.status("Processing CNV assay.")

        self.sample.reset("cnv")

        reads = self.sample.cnv.get_attribute('read_counts', constraint='row+col')
        working_amplicons = (reads.median() > 0).values
        self.sample.cnv = self.sample.cnv[:, working_amplicons]

    def prepare(self):
        assay = self.sample.cnv
        args = self.arguments

        interface.status(f'Preparing DNA variants data.')

        assay.normalize_reads()
        assay.compute_ploidy(diploid_cells=self.sample.dna.barcodes(args.diploid_label))
        assay.set_labels(self.sample.dna.get_labels())
        assay.set_palette(self.sample.dna.get_palette())

    def visual(self):

        args = self.arguments
        assay = self.sample.cnv

        kind = args.visual_type[1]

        interface.status(f'Creating {kind}.')

        if kind == args.HEATMAP:
            bo = assay.clustered_barcodes(orderby=args.orderby)
            if not args.cluster:
                labels = assay.get_labels()[[np.where(assay.barcodes() == b)[0][0] for b in bo]]
                bo = []
                for lab in pd.unique(labels):
                    bo.extend(assay.barcodes(lab))
                bo = np.array(bo)

            feats = args.features
            if args.features == "arguments":
                feats = assay.clustered_ids(orderby=args.orderby)

            args.fig = assay.heatmap(attribute=args.attribute, bars_order=bo, features=feats, convolve=args.convolve)
