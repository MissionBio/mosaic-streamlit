import interface

from .arguments import Arguments
from .render import Render
from .compute import Compute


class Steps():
    """
    The function of this class is to store the steps
    required to process the assay.

    Only the run method should be required to be called.
    When the run method is called, it must process all
    the steps with the latest user provided arguments.
    """

    def __init__(self, sample):
        self._original_sample = sample
        self.sample = sample
        self.arguments = Arguments(sample)
        self.render = Render(sample, self.arguments)
        self.compute = Compute(sample, self.arguments)
        self.initializing = True

    def run(self):
        self.preprocess()
        self.prepare()
        self.visual()

        # After all steps have been performed at least once it will call them only when required.
        self.initializing = False

        interface.status('Done.')

    def preprocess(self):
        clicked = self.render.preprocess()
        if self.initializing:
            self.compute.preprocess()
            self.arguments.save()
        elif clicked:
            self.compute.preprocess()
            self.arguments.save()
            interface.rerun()

    def prepare(self):
        clicked = self.render.prepare()
        if self.initializing:
            self.compute.prepare()
            self.arguments.save()
        if clicked:
            self.compute.prepare()
            self.arguments.save()
            interface.rerun()

    def visual(self):
        self.render.layout()
        self.compute.visual()

        self.render.visual_arguments()
        self.render.visual()
