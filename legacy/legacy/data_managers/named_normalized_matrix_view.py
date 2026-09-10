"""
NamedNormalizedMatrixView module.

Provides a lightweight named view over an existing NormalizedMatrix instance,
allowing users to access matrix columns by meaningful string names instead of
integer indices.

This view maintains a one-to-one mapping between unique column names and
columns of the underlying matrix, delegating most operations back to the
NormalizedMatrix. It enables intuitive name-based interaction while preserving
direct access to the original matrix data.

Typical usage includes:
- Initializing with a NormalizedMatrix and corresponding unique column names.
- Retrieving normalized or original column data by name.
- Appending new rows or removing existing rows by delegating to the matrix.
- Setting and getting normalization bounds on numeric columns by name.

Raises
------
ValueError
    If the number of column names does not match the number of matrix columns
    or if column names are not unique.
"""

from typing import Sequence, Union, List
from paxplot.legacy.data_managers.normalized_matrix import (
    NormalizedMatrix,
    ColumnType,
)
from paxplot.legacy.data_managers.numeric_normalized_array import NumericNormalizedArray
from paxplot.legacy.data_managers.categorical_normalized_array import CategoricalNormalizedArray
from paxplot.legacy.data_managers.base_normalized_array import BaseNormalizedArray

class NamedNormalizedMatrixView:
    """
    A lightweight named view over an existing NormalizedMatrix.

    Parameters
    ----------
    matrix : NormalizedMatrix
        The underlying matrix instance.
    column_names : Sequence[str]
        Unique names corresponding to columns in the matrix.

    Raises
    ------
    ValueError
        If number of names doesn't match number of columns or if names aren't unique.
    """

    def __init__(self, matrix: NormalizedMatrix, column_names: Sequence[str]):
        if not isinstance(column_names, Sequence) or not all(
            isinstance(n, str) for n in column_names
        ):
            raise TypeError("column_names must be a sequence of strings.")
        if matrix.num_columns != len(column_names):
            raise ValueError("Number of names must match matrix columns.")
        if len(set(column_names)) != len(column_names):
            raise ValueError("Column names must be unique.")

        self._matrix = matrix
        self._name_to_index = {
            name: idx for idx, name in enumerate(column_names)
        }
        self._index_to_name = list(column_names)

    @property
    def column_names(self) -> List[str]:
        """Get the list of column names in order.

        Returns
        -------
        List[str]
            The list of column names.
        """
        return self._index_to_name.copy()

    def set_column_names(self, new_names: Sequence[str]) -> None:
        """Set all column names at once.

        Parameters
        ----------
        new_names : Sequence[str]
            The new column names to set.

        Raises
        ------
        TypeError
            If new_names is not a sequence of strings.
        ValueError
            If the number of new names does not match the number of columns.
        ValueError
            If the new names are not unique.
        """
        if not isinstance(new_names, Sequence) or not all(isinstance(n, str) for n in new_names):
            raise TypeError("new_names must be a sequence of strings.")
        if len(new_names) != self._matrix.num_columns:
            raise ValueError(
                f"Number of new names ({len(new_names)}) must match matrix columns "
                f"({self._matrix.num_columns})."
            )
        if len(set(new_names)) != len(new_names):
            raise ValueError("All column names must be unique.")

        self._index_to_name = list(new_names)
        self._name_to_index = {name: idx for idx, name in enumerate(self._index_to_name)}

    @property
    def matrix(self) -> NormalizedMatrix:
        """
        Returns the underlying NormalizedMatrix instance.

        Returns
        -------
        NormalizedMatrix
            The wrapped normalized matrix.
        """
        return self._matrix

    def _get_index(self, column_name: str) -> int:
        """
        Map a column name to its integer index.

        Parameters
        ----------
        column_name : str
            The name of the column.

        Returns
        -------
        int
            The integer index of the column.

        Raises
        ------
        KeyError
            If the column name does not exist.
        """
        if column_name not in self._name_to_index:
            raise KeyError(f"Column '{column_name}' not found.")
        return self._name_to_index[column_name]

    def get_column_name(self, column_index: int) -> str:
        """
        Get the name of a column by index.

        Parameters
        ----------
        column_index : int
            The integer index of the column.

        Returns
        -------
        str
            The column name.

        Raises
        ------
        IndexError
            If the column_index is out of range.
        """
        if column_index < 0 or column_index >= len(self._index_to_name):
            raise IndexError("Column index out of range.")
        return self._index_to_name[column_index]

    def get_column_index(self, column_name: str) -> int:
        """
        Get the index of a column by name.

        Parameters
        ----------
        column_name : str
            The name of the column.

        Returns
        -------
        int
            The integer index of the column.

        Raises
        ------
        KeyError
            If the column name does not exist.
        """
        return self._get_index(column_name)

    def set_column_name(self, column_index: int, new_name: str) -> None:
        """
        Set the name of a column by index.

        Parameters
        ----------
        column_index : int
            The integer index of the column.
        new_name : str
            The new column name. Must be unique.

        Raises
        ------
        IndexError
            If the column_index is out of range.
        ValueError
            If new_name is not a string or not unique.
        """
        if not isinstance(new_name, str):
            raise ValueError("Column name must be a string.")
        if column_index < 0 or column_index >= len(self._index_to_name):
            raise IndexError("Column index out of range.")
        if new_name in self._name_to_index and self._name_to_index[new_name] != column_index:
            raise ValueError(f"Column name '{new_name}' already exists.")

        old_name = self._index_to_name[column_index]
        self._index_to_name[column_index] = new_name
        del self._name_to_index[old_name]
        self._name_to_index[new_name] = column_index

    def __getitem__(self, column_name: str) -> BaseNormalizedArray:
        """
        Get a column by name.

        Parameters
        ----------
        column_name : str
            The name of the column.

        Returns
        -------
        BaseNormalizedArray
            The normalized array object for the specified column name.
        """
        return self._matrix[self._get_index(column_name)]

    def get_numeric_column(self, column_name: str) -> NumericNormalizedArray:
        """
        Get a column as a NumericNormalizedArray by name.

        Parameters
        ----------
        column_name : str
            The name of the column.

        Returns
        -------
        NumericNormalizedArray
            The numeric normalized array for the specified column.

        Raises
        ------
        TypeError
            If the column is not numeric.
        """
        return self._matrix.get_numeric_column(self._get_index(column_name))

    def get_categorical_column(self, column_name: str) -> CategoricalNormalizedArray:
        """
        Get a column as a CategoricalNormalizedArray by name.

        Parameters
        ----------
        column_name : str
            The name of the column.

        Returns
        -------
        CategoricalNormalizedArray
            The categorical normalized array for the specified column.

        Raises
        ------
        TypeError
            If the column is not categorical.
        """
        return self._matrix.get_categorical_column(self._get_index(column_name))

    @property
    def num_columns(self) -> int:
        """
        Returns the number of columns in the matrix.

        Returns
        -------
        int
            The number of columns.
        """
        return self._matrix.num_columns

    @property
    def num_rows(self) -> int:
        """
        Returns the number of rows in the matrix.

        Returns
        -------
        int
            The number of rows.
        """
        return self._matrix.num_rows

    def get_column_type(self, column_name: str) -> ColumnType:
        """
        Retrieve the column type for a specified column name.

        Parameters
        ----------
        column_name : str
            The name of the column.

        Returns
        -------
        ColumnType
            The type of the column (numeric or categorical).
        """
        return self._matrix.get_column_type(self._get_index(column_name))

    def append_data(
        self, new_rows: Sequence[Sequence[Union[str, int, float]]]
    ) -> None:
        """
        Append new rows to the matrix.

        Parameters
        ----------
        new_rows : Sequence of Sequence of (str, int, float)
            Rows to append, each row must have exactly as many columns as the matrix.
        """
        self._matrix.append_data(new_rows)

    def remove_rows(self, indices: Sequence[int]) -> None:
        """
        Remove rows from the matrix at the specified indices.

        Parameters
        ----------
        indices : Sequence[int]
            Indices of rows to remove.
        """
        self._matrix.remove_rows(indices)
