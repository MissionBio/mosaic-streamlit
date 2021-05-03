

def customize(self):
    """
    Compute parameters
    ------------------
    label_map: dict
        The key must be the old label
        and the value the new label.
    palette: dict
        The key must be the name of the
        label and the value the color of
        the cluster.
    """
    self.label_map = {}
    self.palette = self.sample.dna.get_palette()
    self.keep_labs = []
