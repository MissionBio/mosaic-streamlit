from workflows.general.handler import ArgumentsHandler


# There must not be two arguments with the same name

class Arguments(ArgumentsHandler):
    """
    This class is an interface between rendering and
    computation. It must always inherit from the
    ArgumentsHandler class which automates most of
    the functionality required handling parameters.

    All arguments must have a default value. In the
    absence of the Render class, the Compute class
    must be able to run all the steps.

    Any value from this class object that is used
    in the Render or Compute class but not declared
    in one of the methods here will result in a
    workflows.generic.handler.ImplementationError.
    """

    def __init__(self, sample):
        super().__init__(sample, "cnv")

    def preprocess(self):
        """
        Compute Parameters
        ----------
        dp: int
            [0, 100] step=1
        gq: int
            [0, 100] step=1
        af: int
            [0, 100] step=1
        std: int
            [0, 100] step=1
        drop_ids: list
            One or more values of the dna.ids()
        keep_ids: list
            One or more values of the dna.ids()

        Render Parameters
        -----------------
        ids: list
            All the ids in the dna object
        """
        self.percent_cells = 50

    def prepare(self):
        """
        Compute Parameters
        ------------------
        scale_attribute: list
            [AF_MISSING, AF, NGT, NGT_FILTERED, GQ, DP]
        pca_attribute: list
            [AF_MISSING, AF, NGT, NGT_FILTERED, GQ, DP]
        umap_attribute: list
            [AF_MISSING, AF, NGT, NGT_FILTERED, GQ, DP]
        pca_comps: int
            [0, 20] step=1
        """

        self.diploid_label = None

    def layout(self):
        self.visual_type = ["Plots", "Heatmap"]
        self.args_container = None
        self.plot_container = None

    def visual(self):

        self.HEATMAP = "Heatmap"
        self.SCATTERPLOT = "Scatterplot"
        self.LINE_PLOT = "Line plot"

        self.fig = None

        def heatmap():
            self.attribute = "normalized_counts"
            self.splitby = "dna_label"
            self.orderby = "normalized_counts"
            self.cluster = True
            self.features = "positions"
            self.convolve = 0

        heatmap()
