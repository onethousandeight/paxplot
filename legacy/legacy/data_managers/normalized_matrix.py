"""
A matrix class that handles normalization of mixed numeric and categorical data.

This class provides functionality to store and manage a 2D data structure where each column
can be either numeric or categorical. Each column is independently normalized according to
its type. Numeric columns are scaled to a [0,1] range, while categorical columns are
encoded as normalized indicators.

Notes
-----
- Each column must contain consistently typed data (either all numeric or all categorical).
- Null values (None) are not allowed in either numeric or categorical columns.
- Column access is zero-indexed.
"""

from typing import Sequence, Union, List
from enum import Enum
import numpy as np

from paxplot.legacy.data_managers.numeric_normalized_array import NumericNormalizedArray
from paxplot.legacy.data_managers.categorical_normalized_array import CategoricalNormalizedArray
from paxplot.legacy.data_managers.base_normalized_array import BaseNormalizedArray


class ColumnType(str, Enum):
    """Represents the type of a column in the normalized matrix.

    Parameters
    ----------
    ColumnType : Enum
        Represents the type of a column in the normalized matrix.
    """
    NUMERIC = "numeric"
    CATEGORICAL = "categorical"


class NormalizedMatrix:
    """
    A typed, column-oriented matrix that normalizes each column independently.

    Each column is either numeric or categorical and stored as a normalized array.
    Columns are accessed by integer index.

    Notes
    -----
    None values are not allowed in the matrix.
    """

    def __init__(self, data: Sequence[Sequence[Union[str, int, float]]]):
        arr = self.validate_column_shape_and_nulls(data)
        col_types = self.infer_column_types(arr)
        self._columns: List[BaseNormalizedArray] = [
            NumericNormalizedArray(values=arr[:, i].tolist())
            if col_type == ColumnType.NUMERIC
            else CategoricalNormalizedArray(values=arr[:, i].tolist())
            for i, col_type in enumerate(col_types)
        ]

    @staticmethod
    def validate_column_shape_and_nulls(
        rows: Sequence[Sequence[Union[str, int, float]]]
    ) -> np.ndarray:
        """
        Validates that the input is a 2D array-like structure and contains no None values.

        Returns
        -------
        np.ndarray
            The validated array with dtype=object.

        Raises
        ------
        ValueError
            If input is not 2D or contains None values.
        """
        arr = np.array(rows, dtype=object)
        if arr.ndim != 2:
            raise ValueError("Input must be a 2D array-like structure")
        if np.any(arr == None):  # pylint: disable=singleton-comparison
            raise ValueError("Input contains None values, which are not allowed")
        return arr

    @staticmethod
    def infer_column_types(arr: np.ndarray) -> List[ColumnType]:
        """
        Infers column types from a validated 2D ndarray.

        Parameters
        ----------
        arr : np.ndarray
            A validated 2D NumPy array with dtype=object.

        Returns
        -------
        List[ColumnType]
            The inferred column types.

        Raises
        ------
        ValueError
            If a column contains mixed or unsupported types.
        """
        n_cols = arr.shape[1]
        column_types: List[ColumnType] = []

        for col_index in range(n_cols):
            col_data = arr[:, col_index]
            types = {type(x) for x in col_data}

            if types.issubset({int, float}):
                column_types.append(ColumnType.NUMERIC)
            elif types.issubset({str}):
                column_types.append(ColumnType.CATEGORICAL)
            else:
                raise ValueError(
                    f"Column {col_index} contains mixed or unsupported types: {types}"
                )

        return column_types

    def __getitem__(self, column_index: int) -> BaseNormalizedArray:
        """
        Get a column by index.
        
        The returned object may be NumericNormalizedArray or CategoricalNormalizedArray.
        """
        return self._columns[column_index]

    def get_numeric_column(self, column_index: int) -> NumericNormalizedArray:
        """
        Get a column as a NumericNormalizedArray. Raises TypeError if not numeric.
        """
        col = self._columns[column_index]
        if not isinstance(col, NumericNormalizedArray):
            raise TypeError(f"Column {column_index} is not numeric.")
        return col

    def get_categorical_column(self, column_index: int) -> CategoricalNormalizedArray:
        """
        Get a column as a CategoricalNormalizedArray. Raises TypeError if not categorical.
        """
        col = self._columns[column_index]
        if not isinstance(col, CategoricalNormalizedArray):
            raise TypeError(f"Column {column_index} is not categorical.")
        return col

    @property
    def num_columns(self) -> int:
        """Returns the number of columns in the matrix."""
        return len(self._columns)

    @property
    def num_rows(self) -> int:
        """Returns the number of rows in the matrix."""
        if not self._columns:
            return 0
        return len(self._columns[0].values)

    def get_column_type(self, column_index: int) -> ColumnType:
        """
        Retrieve the column type for a specified column index.
        """
        column_instance = self._columns[column_index]
        if isinstance(column_instance, NumericNormalizedArray):
            return ColumnType.NUMERIC
        elif isinstance(column_instance, CategoricalNormalizedArray):
            return ColumnType.CATEGORICAL
        else:
            raise ValueError("Unknown column type")

    def append_data(self, new_rows: Sequence[Sequence[Union[str, int, float]]]) -> None:
        """
        Append one or more new rows to the matrix.

        Raises
        ------
        ValueError
            If dimensions are invalid or None values are present.
        TypeError
            If any value doesn't match expected column type.
        """
        if not new_rows:
            return
        arr = self.validate_column_shape_and_nulls(new_rows)

        if arr.shape[1] != self.num_columns:
            raise ValueError(
                f"Expected {self.num_columns} columns, got {arr.shape[1]}"
            )

        for col_index, col_data in enumerate(arr.T):
            column = self._columns[col_index]
            if isinstance(column, NumericNormalizedArray):
                if not all(isinstance(x, (int, float)) for x in col_data):
                    raise TypeError(f"Column {col_index} expects numeric values")
            elif isinstance(column, CategoricalNormalizedArray):
                if not all(isinstance(x, str) for x in col_data):
                    raise TypeError(f"Column {col_index} expects string values")
            else:
                raise TypeError(f"Unknown column type at index {col_index}")

        for i, column in enumerate(self._columns):
            column.append_array(arr[:, i].tolist())

    def remove_rows(self, indices: Sequence[int]) -> None:
        """
        Remove rows from the matrix at the specified indices.

        Raises
        ------
        TypeError
            If indices are not a sequence of integers.
        IndexError
            If any index is out of bounds.
        """
        if not isinstance(indices, Sequence) or not all(isinstance(i, int) for i in indices):
            raise TypeError("Indices must be a sequence of integers.")

        if not indices:
            return

        if any(i < 0 or i >= self.num_rows for i in indices):
            raise IndexError("One or more indices are out of bounds.")

        for column in self._columns:
            column.remove_indices(indices)
