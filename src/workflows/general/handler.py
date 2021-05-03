
import numpy as np


class ImplementationError(Exception):
    def __init__(self, key, save=False, repeat=False):
        if save:
            message = f"\"{key}\" was not saved in the metadata. It must be of type {ArgumentsHandler.STORED_TYPES}"
        elif repeat:
            message = f"\"{key}\" was used for two different argument names. Make sure each argument is unique."
        else:
            message = f"\"{key}\" was not initialized in the Arguments class."
            message += " Please read the documents to understand the implementation requirements."
        super().__init__(message)


class ArgumentsHandler():
    """
    This class has is used to store the parameters
    in the h5 file
    """

    STORED_TYPES = (str, int, float, list, np.ndarray)
    EXC_ATTR = ["get", "metakey", "save", "attributes"]

    def __init__(self, sample, selected_assay):
        self.sample = sample
        self.assaykey = selected_assay
        self._init_attrs = set()
        assay = getattr(self.sample, f"_original_{self.assaykey}")

        # Initialize all variables with the defaults
        for key in dir(self):
            if not key.startswith("__") and key not in self.EXC_ATTR:
                val = getattr(self, key)
                self._init_attrs |= set(dir(self))
                if callable(val):
                    val()

        # Store variables in the h5 file
        # If already present use the stored value
        attributes = []
        for key in dir(self):
            if not key.startswith("__") and key not in self.EXC_ATTR:
                val = getattr(self, key)
                mkey = self.metakey(key)
                attributes.append(key)

                if isinstance(val, self.STORED_TYPES):
                    if mkey not in assay.metadata:
                        assay.add_metadata(mkey, val)
                    else:
                        setattr(self, key, assay.metadata[mkey])

        self.attributes = attributes + ["attributes", "_init_attrs"]

    def __setattr__(self, name, value):
        """
        Check that the no new attributes are fetched
        """

        if "attributes" in dir(self):
            if name not in self.attributes:
                raise ImplementationError(name)
        elif "_init_attrs" in dir(self) and name in self._init_attrs and name != "_init_attrs":
            raise ImplementationError(name, repeat=True)

        super().__setattr__(name, value)

    def __getattr__(self, name):
        """
        Check that the no new attributes are fetched
        """

        if "attributes" in dir(self) and name not in self.attributes:
            raise ImplementationError(name)

        super().__getattr__(name)

    def get(self, key):
        """
        Retrieve the value from the h5 file
        """

        if key not in self.attributes:
            raise ImplementationError(key)

        assay = getattr(self.sample, f"_original_{self.assaykey}")
        mkey = self.metakey(key)

        if mkey not in assay.metadata:
            raise ImplementationError(key, save=True)
        val = assay.metadata[mkey]

        return val

    def metakey(self, key):
        """
        The key with which the data is to be stored
        in the assay metadata. This mapping is done
        to ensure unique keys and to prevent and
        overwritting of data.
        """

        return f"__mosaic_{self.assaykey}_{key}"

    def save(self):
        """
        Stores all the current arguments in the h5 file
        """
        assay = getattr(self.sample, f"_original_{self.assaykey}")
        for key in dir(self):
            if not key.startswith("__") and key not in self.EXC_ATTR:
                val = getattr(self, key)
                mkey = self.metakey(key)

                if key not in self.attributes:
                    raise ImplementationError(key)

                if isinstance(val, self.STORED_TYPES):
                    assay.add_metadata(mkey, val)
