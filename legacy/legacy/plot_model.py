"""
Module providing the PlotModel class for managing and interacting with
normalized tabular data.

PlotModel wraps a NormalizedMatrix to enable operations such as adding,
removing, and accessing rows of mixed-type data with numeric and categorical
columns. It supports normalization, raw data access, and custom bounds setting.

Additionally, PlotModel can maintain column names through a NamedNormalizedMatrixView,
allowing intuitive access to columns by name as well as by index.

Typical usage:
- Initialize with initial data.
- Append or remove rows dynamically.
- Access normalized or raw data columns by index or name.
- Set and get custom normalization bounds for numeric columns.
- Define and manage unique column names for improved readability.
"""

from typing import Sequence, Union, List, Optional

import numpy as np
from numpy.typing import NDArray

from paxplot.legacy.data_managers.normalized_matrix import NormalizedMatrix
from paxplot.legacy.data_managers.named_normalized_matrix_view import NamedNormalizedMatrixView
from paxplot.legacy.plot_component_managers.tick_collection import TickCollection


class PlotModel:
    """
    A plot model that manages data via a NormalizedMatrix.

    Focuses on data operations: adding, appending, and removing rows,
    as well as accessing normalized and raw column data, and setting custom bounds.
    """

    def __init__(self, data: Sequence[Sequence[Union[str, int, float]]]):
        """
        Initialize PlotModel with initial data.

        Parameters
        ----------
        data : Sequence of rows with mixed-type values
            Initial data to populate the normalized matrix.
        """
        self._matrix = NormalizedMatrix(data=data)
        self._named_view: Optional[NamedNormalizedMatrixView] = None
        self._tick_collection = TickCollection(self._matrix)

    @property
    def num_rows(self) -> int:
        """Number of rows in the data."""
        return self._matrix.num_rows

    @property
    def num_columns(self) -> int:
        """Number of columns in the data."""
        return self._matrix.num_columns



    def get_column_values_normalized(self, column_index: int) -> NDArray[np.float64]:
        """
        Get the normalized data for the specified column.

        Parameters
        ----------
        column_index : int

        Returns
        -------
        Sequence[float]
            The normalized values for the column.
        """
        return self._matrix[column_index].values_normalized

    def get_column_values(self, column_index: int) -> Sequence[Union[str, int, float]]:
        """
        Get the original raw (unnormalized) data for the specified column.

        Parameters
        ----------
        column_index : int

        Returns
        -------
        Sequence[Union[str, int, float]]
            The raw data values for the column.
        """
        return self._matrix[column_index].values

    def get_column_custom_max(self, column_index: int) -> float | None:
        """
        Get the custom maximum bound for the specified numeric column.

        Parameters
        ----------
        column_index : int

        Returns
        -------
        float | None
            The custom maximum bound, or None if not set.
        """
        return self._matrix.get_numeric_column(column_index).custom_max_val

    def get_column_custom_min(self, column_index: int) -> float | None:
        """
        Get the custom minimum bound for the specified numeric column.

        Parameters
        ----------
        column_index : int

        Returns
        -------
        float | None
            The custom minimum bound, or None if not set.
        """
        return self._matrix.get_numeric_column(column_index).custom_min_val

    def get_column_effective_min(self, column_index: int) -> float | None:
        """
        Get the effective minimum bound for the specified numeric column.

        Parameters
        ----------
        column_index : int

        Returns
        -------
        float | None
            The effective minimum bound, or None if not set.
        """
        return self._matrix.get_numeric_column(column_index).effective_min_val

    def get_column_effective_max(self, column_index: int) -> float | None:
        """
        Get the effective maximum bound for the specified numeric column.

        Parameters
        ----------
        column_index : int

        Returns
        -------
        float | None
            The effective maximum bound, or None if not set.
        """
        return self._matrix.get_numeric_column(column_index).effective_max_val

    def set_custom_bounds(
        self,
        column_index: int,
        min_val: float | None = None,
        max_val: float | None = None
    ) -> None:
        """
        Set custom min and/or max bounds for the numeric column.

        Parameters
        ----------
        column_index : int
        min_val : float | None
            Custom minimum bound for normalization, or None to leave unchanged.
        max_val : float | None
            Custom maximum bound for normalization, or None to leave unchanged.

        Raises
        ------
        TypeError
            If the specified column is not numeric.
        """
        self._matrix.get_numeric_column(column_index).set_custom_bounds(min_val, max_val)

    def append_rows(self, new_rows: Sequence[Sequence[Union[str, int, float]]]) -> None:
        """
        Append new rows to the existing data.

        Parameters
        ----------
        new_rows : Sequence of rows with mixed-type values
        """
        self._matrix.append_data(new_rows)

    def remove_rows(self, indices: Sequence[int]) -> None:
        """
        Remove rows by indices.

        Parameters
        ----------
        indices : Sequence of row indices to remove
        """
        self._matrix.remove_rows(indices)

    # Methods for accessing named columns

    def set_column_names(self, column_names: Sequence[str]) -> None:
        """
        Set all column names at once.

        Parameters
        ----------
        column_names : Sequence[str]
            New list of column names, must match matrix column count and be unique.

        Raises
        ------
        ValueError
            If length mismatch or duplicate names found.
        TypeError
            If any name is not a string.
        """
        if self._named_view is None:
            # create NamedNormalizedMatrixView with names
            self._named_view = NamedNormalizedMatrixView(self._matrix, column_names)
        else:
            self._named_view.set_column_names(column_names)

    def get_column_names(self) -> List[str]:
        """
        Get the list of column names.

        Returns
        -------
        List[str]
            List of column names.

        Raises
        ------
        RuntimeError
            If column names have not been set.
        """
        if self._named_view is None:
            raise RuntimeError("Column names have not been set.")
        return self._named_view.column_names

    def get_column_name(self, column_index: int) -> str:
        """
        Get the name of a column by index.

        Raises
        ------
        RuntimeError
            If column names have not been set.
        """
        if self._named_view is None:
            raise RuntimeError("Column names have not been set.")
        return self._named_view.get_column_name(column_index)

    def set_column_name(self, column_index: int, new_name: str) -> None:
        """
        Set the name of a column by index.

        Raises
        ------
        RuntimeError
            If column names have not been set.
        """
        if self._named_view is None:
            raise RuntimeError("Column names have not been set.")
        self._named_view.set_column_name(column_index, new_name)

    def get_column_values_normalized_by_name(self, column_name: str) -> NDArray:
        """
        Get the normalized data for the specified column name.

        Raises
        ------
        RuntimeError
            If column names have not been set.
        """
        if self._named_view is None:
            raise RuntimeError("Column names have not been set.")
        return self._named_view[column_name].values_normalized

    def get_column_values_by_name(self, column_name: str) -> Sequence[Union[str, int, float]]:
        """
        Get the original raw (unnormalized) data for the specified column name.

        Raises
        ------
        RuntimeError
            If column names have not been set.
        """
        if self._named_view is None:
            raise RuntimeError("Column names have not been set.")
        return self._named_view[column_name].values

    def set_custom_bounds_by_name(
        self,
        column_name: str,
        min_val: float | None = None,
        max_val: float | None = None
    ) -> None:
        """
        Set custom min and/or max bounds for the numeric column name.

        Raises
        ------
        RuntimeError
            If column names have not been set.
        """
        if self._named_view is None:
            raise RuntimeError("Column names have not been set.")
        self._named_view.get_numeric_column(column_name).set_custom_bounds(min_val, max_val)

    def get_column_custom_max_by_name(self, column_name: str) -> float | None:
        """
        Get the custom maximum bound for the specified numeric column.

        Parameters
        ----------
        column_name : str

        Returns
        -------
        float | None
            The custom maximum bound, or None if not set.
        """
        if self._named_view is None:
            raise RuntimeError("Column names have not been set.")
        return self._named_view.get_numeric_column(column_name).custom_max_val

    def get_column_custom_min_by_name(self, column_name: str) -> float | None:
        """
        Get the custom minimum bound for the specified numeric column.

        Parameters
        ----------
        column_name : str

        Returns
        -------
        float | None
            The custom minimum bound, or None if not set.
        """
        if self._named_view is None:
            raise RuntimeError("Column names have not been set.")
        return self._named_view.get_numeric_column(column_name).custom_min_val

    def get_column_effective_min_by_name(self, column_name: str) -> float | None:
        """
        Get the effective minimum bound for the specified numeric column.

        Parameters
        ----------
        column_name : str

        Returns
        -------
        float | None
            The effective minimum bound, or None if not set.
        """
        if self._named_view is None:
            raise RuntimeError("Column names have not been set.")
        return self._named_view.get_numeric_column(column_name).effective_min_val

    def get_column_effective_max_by_name(self, column_name: str) -> float | None:
        """
        Get the effective maximum bound for the specified numeric column.

        Parameters
        ----------
        column_name : str

        Returns
        -------
        float | None
            The effective maximum bound, or None if not set.
        """
        if self._named_view is None:
            raise RuntimeError("Column names have not been set.")
        return self._named_view.get_numeric_column(column_name).effective_max_val


    def get_numeric_ticks(self, column_index: int) -> List[float]:
        """
        Get raw tick values for a numeric column.

        Parameters
        ----------
        column_index : int
            Index of the column.

        Returns
        -------
        List[float]
            Raw tick values for the numeric column.

        Raises
        ------
        TypeError
            If the column is not numeric.
        """
        return self._tick_collection.get_numeric_tick_manager(column_index).get_raw_values()

    def get_numeric_ticks_normalized(self, column_index: int) -> List[float]:
        """
        Get normalized tick values for a numeric column.

        Parameters
        ----------
        column_index : int
            Index of the column.

        Returns
        -------
        List[float]
            Normalized tick values for the numeric column.

        Raises
        ------
        TypeError
            If the column is not numeric.
        """
        return self._tick_collection.get_numeric_tick_manager(column_index).get_normalized_values()

    def get_categorical_ticks(self, column_index: int) -> List[str]:
        """
        Get tick labels for a categorical column.

        Parameters
        ----------
        column_index : int
            Index of the column.

        Returns
        -------
        List[str]
            Tick labels for the categorical column.

        Raises
        ------
        TypeError
            If the column is not categorical.
        """
        return self._tick_collection.get_categorical_tick_manager(column_index).get_raw_values()

    def get_categorical_ticks_normalized(self, column_index: int) -> List[float]:
        """
        Get normalized tick positions for a categorical column.

        Parameters
        ----------
        column_index : int
            Index of the column.

        Returns
        -------
        List[float]
            Normalized tick positions for the categorical column.

        Raises
        ------
        TypeError
            If the column is not categorical.
        """
        return self._tick_collection.get_categorical_tick_manager(column_index).get_normalized_values()

    def set_numeric_ticks(self, column_index: int, tick_values: List[float]) -> None:
        """
        Set custom tick values for a numeric column.

        Parameters
        ----------
        column_index : int
            Index of the column.
        tick_values : List[float]
            Custom tick values to set.

        Raises
        ------
        TypeError
            If the column is not numeric.
        """
        self._tick_collection.get_numeric_tick_manager(column_index).set_ticks(tick_values)

    def set_categorical_ticks(self, column_index: int, tick_labels: List[str]) -> None:
        """
        Set custom tick labels for a categorical column.

        Parameters
        ----------
        column_index : int
            Index of the column.
        tick_labels : List[str]
            Custom tick labels to set.

        Raises
        ------
        TypeError
            If the column is not categorical.
        """
        self._tick_collection.get_categorical_tick_manager(column_index).set_ticks(tick_labels)

    def get_numeric_ticks_by_name(self, column_name: str) -> List[float]:
        """
        Get raw tick values for a numeric column by name.

        Parameters
        ----------
        column_name : str
            Name of the column.

        Returns
        -------
        List[float]
            Raw tick values for the numeric column.

        Raises
        ------
        RuntimeError
            If column names have not been set.
        TypeError
            If the column is not numeric.
        """
        if self._named_view is None:
            raise RuntimeError("Column names have not been set.")
        column_index = self._named_view.get_column_index(column_name)
        return self.get_numeric_ticks(column_index)

    def get_categorical_ticks_by_name(self, column_name: str) -> List[str]:
        """
        Get tick labels for a categorical column by name.

        Parameters
        ----------
        column_name : str
            Name of the column.

        Returns
        -------
        List[str]
            Tick labels for the categorical column.

        Raises
        ------
        RuntimeError
            If column names have not been set.
        TypeError
            If the column is not categorical.
        """
        if self._named_view is None:
            raise RuntimeError("Column names have not been set.")
        column_index = self._named_view.get_column_index(column_name)
        return self.get_categorical_ticks(column_index)

    def set_numeric_ticks_by_name(self, column_name: str, tick_values: List[float]) -> None:
        """
        Set custom tick values for a numeric column by name.

        Parameters
        ----------
        column_name : str
            Name of the column.
        tick_values : List[float]
            Custom tick values to set.

        Raises
        ------
        RuntimeError
            If column names have not been set.
        TypeError
            If the column is not numeric.
        """
        if self._named_view is None:
            raise RuntimeError("Column names have not been set.")
        column_index = self._named_view.get_column_index(column_name)
        self.set_numeric_ticks(column_index, tick_values)

    def set_categorical_ticks_by_name(self, column_name: str, tick_labels: List[str]) -> None:
        """
        Set custom tick labels for a categorical column by name.

        Parameters
        ----------
        column_name : str
            Name of the column.
        tick_labels : List[str]
            Custom tick labels to set.

        Raises
        ------
        RuntimeError
            If column names have not been set.
        TypeError
            If the column is not categorical.
        """
        if self._named_view is None:
            raise RuntimeError("Column names have not been set.")
        column_index = self._named_view.get_column_index(column_name)
        self.set_categorical_ticks(column_index, tick_labels)
