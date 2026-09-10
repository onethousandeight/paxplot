"""
Base classes for normalized array types.

This module provides abstract base classes to support normalized array data structures.
It includes the `BaseNormalizedArray` abstract class, which defines a consistent interface
for managing raw data sequences stored as Python lists and producing normalized NumPy arrays
scaled to the range [-1, 1].

Normalization logic is delegated to an internal `ArrayNormalizer` instance, which subclasses
must initialize appropriately.

The module depends on NumPy for numerical array operations and may utilize Pydantic
for validation in related components.
"""

from abc import ABC, abstractmethod
from typing import Any, Sequence, Callable, List, TypeVar, Generic
import numpy as np
from numpy.typing import NDArray
from paxplot.legacy.data_managers.array_normalizer import ArrayNormalizer

T = TypeVar("T")

class BaseNormalizedArray(ABC, Generic[T]):
    """
    Abstract base class for normalized arrays.

    This class provides a common interface and partial implementation for
    normalized array types. Raw values are always stored internally as a
    mutable Python ``list`` of elements, while normalized values are returned
    as a NumPy ``ndarray`` scaled to the range [-1, 1].

    An internal :class:`ArrayNormalizer` instance handles the normalization
    process, ensuring consistent scaling behavior across subclasses.

    Subclasses must implement methods for appending data and removing elements
    by index, as well as providing the correct normalizer type.

    Parameters
    ----------
    values : Sequence[T]
        The raw input data sequence to be stored and normalized.

    Attributes
    ----------
    values : list[T]
        Raw values stored internally as a Python list.
    _normalizer : ArrayNormalizer
        Internal instance responsible for normalization operations.
    """

    values: List[T]
    _normalizer: ArrayNormalizer

    def __init__(self, values: Sequence[T]):
        self.values = list(values)
        self._normalizer = self._init_normalizer()

    @property
    def custom_min_val(self) -> float | None:
        """
        The custom minimum value used for normalization, if any.

        Returns
        -------
        float | None
            The user-specified minimum value, or None if not set.
        """
        return self._normalizer.custom_min_val

    @property
    def custom_max_val(self) -> float | None:
        """
        The custom maximum value used for normalization, if any.

        Returns
        -------
        float | None
            The user-specified maximum value, or None if not set.
        """
        return self._normalizer.custom_max_val

    @property
    def effective_min_val(self) -> float:
        """
        The effective minimum value used for normalization.

        This is usually ``custom_min_val`` if set, otherwise derived from the data.

        Returns
        -------
        float
            Effective minimum value.
        """
        return self._normalizer.effective_min_val

    @property
    def effective_max_val(self) -> float:
        """
        The effective maximum value used for normalization.

        This is usually ``custom_max_val`` if set, otherwise derived from the data.

        Returns
        -------
        float
            Effective maximum value.
        """
        return self._normalizer.effective_max_val

    @abstractmethod
    def _init_normalizer(self) -> ArrayNormalizer:
        """
        Subclasses must return the appropriate :class:`ArrayNormalizer` instance
        for their data type.

        Returns
        -------
        ArrayNormalizer
            The normalizer instance for this array type.
        """
        ...  # pylint: disable=W2301

    def __len__(self) -> int:
        return len(self.values)

    def __getitem__(self, index: int) -> Any:
        return self.values[index]

    @property
    def values_normalized(self) -> NDArray[np.float64]:
        """
        The normalized data values as a NumPy array scaled to [-1, 1].

        The raw values are first normalized by the internal normalizer
        according to the current effective min/max values.

        Returns
        -------
        NDArray[np.float64]
            A NumPy array of normalized float64 values.
        """
        return self._normalizer.array_normalized

    @abstractmethod
    def append_array(self, new_data: Sequence[Any]) -> None:
        """
        Appends new data elements to the existing array and updates normalization.

        Subclasses must implement how new data is added and how normalization
        state is updated accordingly.

        Parameters
        ----------
        new_data : Sequence[Any]
            New elements to append to the array.
        """
        ...  # pylint: disable=W2301

    def remove_indices(self, indices: Sequence[int]) -> None:
        """
        Remove elements at the specified indices from the raw values list
        and update the internal normalization state.

        Parameters
        ----------
        indices : Sequence[int]
            Sequence of integer indices indicating which elements to remove.

        Raises
        ------
        TypeError
            If ``indices`` is not a sequence of integers.
        IndexError
            If any index is out of bounds.
        """
        if not isinstance(indices, Sequence):
            raise TypeError("Indices must be a sequence of integers.")
        index_array = np.array(indices, dtype=np.int64)
        self._normalizer.remove_indices(index_array)

        # Remove raw entries from `self.array`
        array_np = np.array(self.values)
        mask = np.ones(len(array_np), dtype=bool)
        mask[index_array] = False
        self.values = array_np[mask].tolist()

    def register_observer(self, callback: Callable[[], None]) -> None:
        """
        Registers a callback to be called after normalization is recomputed.
        """
        self._normalizer.register_observer(callback)

    def unregister_observer(self, callback: Callable[[], None]) -> None:
        """
        Unregisters a previously registered observer callback.
        """
        self._normalizer.unregister_observer(callback)
