"""
Defines the NumericNormalizedArray class, a specialized normalized array 
for numeric data (floats and integers).

This module extends the abstract BaseNormalizedArray class to support sequences 
of numeric values stored internally as Python lists and normalized to the range 
[-1, 1] via min-max scaling. It provides concrete implementations for appending 
and updating numeric data, maintaining normalization state efficiently.

Classes
-------
NumericNormalizedArray
    A concrete implementation of BaseNormalizedArray for numeric (int or float) sequences.
"""

from typing import Sequence

from pydantic import validate_call
import numpy as np

from paxplot.legacy.data_managers.base_normalized_array import BaseNormalizedArray
from paxplot.legacy.data_managers.array_normalizer import ArrayNormalizer


class NumericNormalizedArray(BaseNormalizedArray[float | int]):
    """
    A normalized array specifically for numeric (float or int) sequences.

    Raw numeric values are stored internally as a Python list of floats or ints.
    The normalized representation is produced by min-max scaling these values
    to the range [-1, 1] using an internal :class:`ArrayNormalizer`.

    This class provides concrete methods to append new numeric data or replace
    the entire dataset, automatically updating the normalization accordingly.

    Attributes
    ----------
    values : list[float | int]
        Raw numeric values stored internally.
    """

    def _init_normalizer(self) -> ArrayNormalizer:
        """
        Initialize the internal ArrayNormalizer with the current raw numeric values.

        Returns
        -------
        ArrayNormalizer
            The normalizer instance configured with the numeric data.
        """
        arr = np.array(self.values, dtype=np.float64)
        return ArrayNormalizer(array=arr)

    @validate_call
    def append_array(self, new_data: Sequence[float | int]) -> None:
        """
        Append new numeric data to the raw values list and update normalization.

        Parameters
        ----------
        new_data : Sequence[float | int]
            A sequence of numeric values to append.

        Raises
        ------
        TypeError
            If the input is not a sequence of numeric values.
        """
        new_array = np.array(new_data, dtype=np.float64)
        self._normalizer.append_array(new_array)
        self.values = list(self.values) + list(new_data)

    @validate_call
    def update_array(self, new_data: Sequence[float | int]) -> None:
        """
        Replace the current raw numeric values with a new sequence and update normalization.

        Parameters
        ----------
        new_data : Sequence[float | int]
            A sequence of numeric values to replace the current array.

        Raises
        ------
        TypeError
            If the input is not a sequence of numeric values.
        """
        new_array = np.array(new_data, dtype=np.float64)
        self._normalizer.update_array(new_array)
        self.values = list(new_data)

    @validate_call
    def set_custom_bounds(self, min_val: float | None = None, max_val: float | None = None) -> None:
        """
        Set custom minimum and/or maximum bounds for normalization and update the normalized array.

        Parameters
        ----------
        min_val : float | None
            Custom minimum value for normalization.
        max_val : float | None
            Custom maximum value for normalization.
        """
        self._normalizer.set_custom_bounds(min_val=min_val, max_val=max_val)
