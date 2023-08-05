import cPickle


def load(filepath):
    """Load a pickled object from a pickle file using the faster cPickle

    Parameters
    ----------
    filepath: str
        The filepath to extract a pickle from

    Returns
    -------
    object
    """
    with open(filepath, 'rb') as f:
        return cPickle.load(f)


def dump(obj, filepath):
    """Dump the obj to a pickle file using the quicker cPickle

    Parameters
    ----------
    obj: object
        The object to pickle
    filepath: str
        The filepath to dump the pickled object to
    """
    with open(filepath, 'wb') as f:
        cPickle.dump(obj, f, cPickle.HIGHEST_PROTOCOL)