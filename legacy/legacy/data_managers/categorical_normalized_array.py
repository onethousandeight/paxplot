"""
Categorical normalized array class for handling and normalizing string data.

This module defines the `CategoricalNormalizedArray` class, a concrete
implementation of `BaseNormalizedArray` designed for categorical string data.

Raw categorical values are stored internally as a Python list of strings,
while normalization maps these categories to numeric indices which are
scaled to [-1, 1] using an internal `ArrayNormalizer`.

The class manages an ordered list of unique categories and updates normalization
when new data is appended or the array is replaced.
"""

from typing import Sequence, List
import numpy as np
from numpy.typing import NDArray
from pydantic import PrivateAttr, ConfigDict
from paxplot.legacy.data_managers.array_normalizer import ArrayNormalizer
from paxplot.legacy.data_managers.base_normalized_array import BaseNormalizedArray


class CategoricalNormalizedArray(BaseNormalizedArray[str]):
    """
    A normalized array class for categorical (string) data.

    Raw categorical values are stored as a Python list of strings.
    Unique categories are tracked in the order of appearance.
    Normalization maps these categories to numeric indices internally
    and scales them to the range [-1, 1].

    Attributes
    ----------
    values : list[str]
        Raw categorical string values stored internally.
    _categories : list[str]
        Ordered list of unique category labels.
    """

    _categories: List[str] = PrivateAttr(default_factory=list)
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def _init_normalizer(self) -> ArrayNormalizer:
        """
        Initialize the internal ArrayNormalizer by mapping categorical strings
        to numeric indices based on the order of categories.

        Returns
        -------
        ArrayNormalizer
            The normalizer initialized with numeric indices derived from categorical data.
        """
        categories = []
        for category in self.values:
            if category not in categories:
                categories.append(category)
        self._categories = categories

        indices = np.array(
            [categories.index(category) for category in self.values],
            dtype=np.float64
        )
        return ArrayNormalizer(array=indices)

    @property
    def value_indices(self) -> NDArray[np.float64]:
        """
        Numeric index array corresponding to the original categorical values.

        Returns
        -------
        NDArray[np.float64]
            NumPy array of category indices as float64 values.
        """
        return self._normalizer.array

    @property
    def categories(self) -> List[str]:
        """
        List of unique categories in the order they appear.

        Returns
        -------
        List[str]
            Unique category labels.
        """
        return self._categories

    def append_array(self, new_data: Sequence[str]) -> None:
        """
        Append new categorical string values and update normalization.

        Parameters
        ----------
        new_data : Sequence[str]
            New categorical strings to append.
        """
        categories = self._categories
        indices = []
        for category in new_data:
            if category not in categories:
                categories.append(category)
            indices.append(categories.index(category))

        new_index_array = np.array(indices, dtype=np.float64)

        self.values = list(self.values) + list(new_data)
        self._normalizer.append_array(new_index_array)

    def update_array(self, new_data: Sequence[str]) -> None:
        """
        Replace the current categorical array with new data,
        rebuild categories, and update normalization.

        Parameters
        ----------
        new_data : Sequence[str]
            New categorical strings to replace the current array.
        """
        categories = []
        for category in new_data:
            if category not in categories:
                categories.append(category)
        self._categories = categories
        self.values = list(new_data)

        indices = np.array([categories.index(category) for category in new_data], dtype=np.float64)
        self._normalizer.update_array(indices)
