"""Default datasets included with PaxPlot."""

from importlib import resources


def tradeoff():
    """
    Trade-off dataset

    Returns
    -------
    stream : io.BufferedReader
        Stream of trade-off dataset
    """
    return (resources.files(__package__) / "data" / "tradeoff.csv").open("rb")


def hydroclimate_model_evaluation():
    """
    Hydroclimate model evaluation dataset from Nele Reyniers

    Returns
    -------
    stream : io.BufferedReader
        Stream of hydroclimate model evaluation dataset
    """
    return (
        resources.files(__package__) / "data" / "hydroclimate_model_evaluation.csv"
    ).open("rb")
