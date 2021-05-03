import interface
import streamlit as st


class Render():
    """
    The function of this class to read the arguments
    from the Argument class and create an appropriate
    GUI for them. It must also provide feedback to the
    Compute class as to whether the step is to be
    processed or not.
    """

    LAYERS = ["normalized_counts", "ploidy"]

    def __init__(self, sample, arguments):
        self.sample = sample
        self.arguments = arguments

    def preprocess(self):
        args = self.arguments
        with st.sidebar.beta_expander("Preprocessing"):
            args.percent_cells = st.slider("% Cells with amplicon", min_value=0, max_value=100, value=args.get("percent_cells"))
            clicked = st.button("Process")

            return clicked

    def prepare(self):

        args = self.arguments

        with st.sidebar.beta_expander("Data preparation"):
            args.diploid_label = st.selectbox("Diploid cells", list(set(self.sample.dna.get_labels())))

            clicked = st.button("Prepare")

        return clicked

    def layout(self):

        args = self.arguments

        VISUAL_CATEGORY_1 = "Plots"

        VISUALS = {
            VISUAL_CATEGORY_1: [
                [2.3, 1, 1.1, 1.45, 1, 1, 1],
                [args.HEATMAP, args.SCATTERPLOT, args.LINE_PLOT],
            ]
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

        DNA_LABEL = "dna_label"
        PROTEIN_LABEL = "protein_label"
        SPLITBY = [DNA_LABEL, PROTEIN_LABEL, "sample_name", None]

        kind = args.visual_type[1]

        with args.args_container:
            if kind == args.HEATMAP:
                args.attribute = st.selectbox("Attribute", self.LAYERS, key="Visualization Attribute")
                args.splitby = st.selectbox("Split by", SPLITBY)
                args.orderby = st.selectbox("Order by", self.LAYERS, key="Visualization Orderby")
                args.features = st.selectbox("Feature", ["positions", "genes", "amplicons"])
                args.cluster = st.checkbox("Cluster within labels", True)
                args.convolve = st.slider("Smoothing", 0, 100)

    def visual(self):

        args = self.arguments

        with args.plot_container:
            st.plotly_chart(args.fig)
