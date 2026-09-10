"""The ArrayNormalizer class"""

from typing import Any, Type, Callable, List

import numpy as np
from numpy.typing import NDArray
from pydantic import BaseModel, field_validator, model_validator, ConfigDict


class ArrayNormalizer(BaseModel):
    """
    Class to normalize arrays
    """

    array: NDArray[np.float64]
    custom_min_val: float | None = None
    custom_max_val: float | None = None
    _array_normalized: NDArray[np.float64] | None = None
    _effective_min_val: float | None = None
    _effective_max_val: float | None = None
    _observers: List[Callable[[], None]] = []
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @property
    def array_normalized(self) -> NDArray[np.float64]:
        """
        Returns the normalized version of the input array, scaled to the range [-1, 1].

        Returns
        -------
        NDArray[np.number]
            A NumPy array where the values have been normalized using min-max scaling.

        Raises
        ------
        AssertionError
            If normalization has not yet been computed.
        """
        if self._array_normalized is None:
            raise ValueError("Normalization has not been computed yet")
        return self._array_normalized

    @property
    def effective_min_val(self) -> float:
        """
        Returns the effective minimum value used for normalization (defaults to custom).

        Raises
        ------
        ValueError
            If normalization has not yet been computed.
        """
        if self._effective_min_val is None:
            raise ValueError("Normalization has not been computed yet")
        return self._effective_min_val

    @property
    def effective_max_val(self) -> float:
        """
        Returns the effective maximum value used for normalization (defaults to custom).

        Raises
        ------
        ValueError
            If normalization has not yet been computed.
        """
        if self._effective_max_val is None:
            raise ValueError("Normalization has not been computed yet")
        return self._effective_max_val

    @field_validator("array", mode="before")
    @classmethod
    def validate_numpy_array(cls: Type[Any], v: Any) -> NDArray[np.float64]:
        """
        Validates that the input is a 1D NumPy array with a numeric data type.

        Parameters
        ----------
        cls : Type[Any]
            The class this validator belongs to (automatically passed by Pydantic).
        v : Any
            The input value to validate.

        Returns
        -------
        NDArray[np.float64]
            The validated 1D numeric NumPy array.

        Raises
        ------
        ValueError
            If the input is not a NumPy array.
        ValueError
            If the array is not one-dimensional.
        ValueError
            If the array's data type is not numeric (e.g., float, int).
        """

        if not isinstance(v, np.ndarray):
            raise ValueError(
                f"`array` must be a NumPy array, got {type(v).__name__}"
            )

        shape: tuple[int, ...] = v.shape
        if len(shape) != 1:
            raise ValueError(f"`array` must be 1D, got shape {shape}")

        dtype: np.dtype = v.dtype
        if not np.issubdtype(dtype, np.number):
            raise ValueError(f"`array` dtype must be numeric, got {dtype}")

        return v.astype(np.float64)

    @model_validator(mode="after")
    def normalize_after_init(self) -> "ArrayNormalizer":
        """
        Recomputes the normalized array and value bounds after model initialization.

        Returns
        -------
        ArrayNormalizer
            The updated model instance with normalization results populated.
        """
        self._recompute_normalization()
        return self

    def register_observer(self, callback: Callable[[], None]) -> None:
        """
        Registers a callback function to be called after normalization is recomputed.
        The callback should accept no arguments.
        """
        self._observers.append(callback)

    def unregister_observer(self, callback: Callable[[], None]) -> None:
        """
        Unregisters a previously registered callback.
        """
        self._observers.remove(callback)

    def _notify_observers(self) -> None:
        """
        Calls all registered observer callbacks.
        """
        for callback in self._observers:
            callback()

    def _recompute_normalization(self) -> None:
        """
        Computes the normalized array (`_array_normalized`) and stores the
        min and max values used in the normalization.

        If the array has constant values, sets the normalized array to zeros.
        """
        min_val = (
            self.custom_min_val
            if self.custom_min_val is not None
            else float(np.min(self.array))
        )

        max_val = (
            self.custom_max_val
            if self.custom_max_val is not None
            else float(np.max(self.array))
        )

        self._effective_min_val = min_val
        self._effective_max_val = max_val

        if max_val == min_val:
            self._array_normalized = np.zeros_like(self.array, dtype=np.float64)
        else:
            self._array_normalized = self._normalize_to_minus1_plus1(
                self.array, min_val, max_val
            )

        self._notify_observers()

    @staticmethod
    def _normalize_to_minus1_plus1(
        array: NDArray[np.number], min_val: float, max_val: float
    ) -> NDArray[np.float64]:
        """
        Normalizes a NumPy array to the range [-1, 1] using the provided min and max values.

        Parameters
        ----------
        array : NDArray[np.number]
            Input array to normalize.
        min_val : float
            Minimum possible value in the original scale.
        max_val : float
            Maximum possible value in the original scale.

        Returns
        -------
        NDArray[np.number]
            Normalized array in the range [-1, 1].
        """
        array_float = array.astype(np.float64)
        scale = 2.0 / (max_val - min_val)
        return scale * (array_float - min_val) - 1.0


    def update_array(self, new_array: NDArray[np.number]) -> None:
        """
        Updates the internal array with a new NumPy array and re-applies normalization.

        Parameters
        ----------
        new_array : NDArray[np.number]
            A 1D numeric NumPy array to replace the existing array.
        """
        self.array = self.validate_numpy_array(new_array)
        self._recompute_normalization()

    def append_array(self, new_data: NDArray[np.number]) -> None:
        """
        Appends new data to the internal array and updates the normalized array.

        If the new data falls outside the current normalization bounds, the entire
        array is re-normalized. Otherwise, only the new portion is normalized and
        appended to the existing normalized array.

        Parameters
        ----------
        new_data : NDArray[np.number]
            A 1D NumPy array of numeric values to be appended.

        Raises
        ------
        ValueError
            If normalization has not yet been computed (i.e., _array_normalized is None).
        ValueError
            If the input array is invalid (non-numeric, multi-dimensional, etc.).
        """
        validated = self.validate_numpy_array(new_data)
        new_min = float(np.min(validated))
        new_max = float(np.max(validated))
        combined = np.concatenate([self.array, validated])

        if new_min < self.effective_min_val or new_max > self.effective_max_val:
            self.array = combined
            self._recompute_normalization()
        else:
            new_norm = self._normalize_to_minus1_plus1(
                validated,
                self.effective_min_val,
                self.effective_max_val,
            )
            self.array = combined
            if self._array_normalized is None:
                raise ValueError("Normalization must be computed before appending")
            self._array_normalized = np.concatenate([
                self._array_normalized,
                new_norm
            ])

    def remove_indices(self, indices: NDArray[np.integer]) -> None:
        """
        Removes elements at the specified indices from the internal array.
        If any removed elements are equal to the effective min or max values,
        the normalization is recomputed.

        Parameters
        ----------
        indices : NDArray[np.integer]
            1D array of integer indices indicating which elements to remove.

        Raises
        ------
        ValueError
            If normalization has not been computed yet.
            If any index is out of bounds.
        """
        if self._array_normalized is None:
            raise ValueError("Normalization must be computed before removing elements")

        # Validate indices array type and shape
        indices = np.asarray(indices)
        if indices.ndim != 1 or not np.issubdtype(indices.dtype, np.integer):
            raise ValueError("Indices must be a 1D array of integers")

        if np.any(indices < 0) or np.any(indices >= self.array.shape[0]):
            raise IndexError("One or more indices are out of bounds")

        # Determine if min or max value is being removed
        values_to_remove = self.array[indices]
        need_renormalize = (
            np.any(values_to_remove == self.effective_min_val) or
            np.any(values_to_remove == self.effective_max_val)
        )

        # Create mask for elements to keep
        mask = np.ones(self.array.shape[0], dtype=bool)
        mask[indices] = False

        # Remove elements from array and normalized array
        self.array = self.array[mask]
        self._array_normalized = self._array_normalized[mask]

        if need_renormalize:
            self._recompute_normalization()


    def set_custom_bounds(
        self, min_val: float | None = None, max_val: float | None = None
    ) -> None:
        """
        Sets custom min and/or max values for normalization and re-applies normalization.

        Parameters
        ----------
        min_val : float | None
            Custom minimum value for normalization.
        max_val : float | None
            Custom maximum value for normalization.
        """
        self.custom_min_val = min_val
        self.custom_max_val = max_val
        self._recompute_normalization()
