import interface


def customize(compute):
    compute.sample = compute._original_sample

    args = compute.arguments
    assay = compute.sample.dna

    label_changed = len(args.label_map) != 0
    color_changed = assay.get_palette() != args.palette

    if label_changed or color_changed:
        assay.rename_labels(args.label_map)
        assay.set_palette(args.palette)

    if set(args.keep_labs) != set(assay.get_labels()):
        compute.sample = compute.sample[assay.barcodes(args.keep_labs)]


def set_label(sample, assay, name):
    lab, pal = _label_map(name)

    if lab not in dir(sample):
        interface.error(f"{name} has not yet been set.")

    lab = getattr(sample, lab)
    pal = getattr(sample, pal)
    assay.set_labels(lab)
    assay.set_palette(pal)


def add_label(sample, assay, name):
    lab, pal = _label_map(name)
    setattr(sample, lab, assay.get_labels())
    setattr(sample, pal, assay.get_palette())


def _label_map(name):
    return f"__mosaic_label_{name}", f"__mosaic_palette_{name}"
