"""Default datasets included with paxplot."""

from __future__ import annotations

from importlib import resources
from typing import BinaryIO


def tradeoff() -> BinaryIO:
    """
    Trade-off dataset

    Returns
    -------
    stream : io.BufferedReader
        Stream of trade-off dataset
    """
    return (resources.files(__package__) / "data" / "tradeoff.csv").open("rb")


def hydroclimate_model_evaluation() -> BinaryIO:
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
