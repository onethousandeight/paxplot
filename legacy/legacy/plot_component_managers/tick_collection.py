"""
Tick Collection for PaxPlot

This module provides the TickCollection class which manages multiple
tick collections for a NormalizedMatrix, automatically creating and updating ticks
when data changes.

The collection maintains a collection of NumericTicks and
CategoricalTicks instances, one for each column in the NormalizedMatrix.
It automatically generates appropriate ticks when data is updated and provides
a unified interface for tick management across all axes.
"""

from typing import List, Optional, Union
from paxplot.legacy.plot_component_managers.numeric_ticks import (
    NumericTicks,
)
from paxplot.legacy.plot_component_managers.categorical_ticks import (
    CategoricalTicks,
)
from paxplot.legacy.data_managers.normalized_matrix import (
    NormalizedMatrix,
    ColumnType,
)


class TickCollection:
    """
    Coordinates multiple tick collections for a NormalizedMatrix.

    This class manages the relationship between NormalizedMatrix columns and their
    corresponding tick collections, providing a unified interface for
    tick management across all axes. It automatically creates and updates
    ticks when data changes.
    """

    def __init__(self, matrix: NormalizedMatrix):
        """
        Initialize the collection with a NormalizedMatrix.

        Parameters
        ----------
        matrix : NormalizedMatrix
            The normalized matrix to coordinate ticks for.
        """
        self._matrix = matrix
        self._tick_managers: List[
            Optional[Union[NumericTicks, CategoricalTicks]]
        ] = []
        self._initialize_tick_managers()

    def _initialize_tick_managers(self) -> None:
        """Initialize ticks for each column based on data type."""
        self._tick_managers.clear()

        for col_idx in range(self._matrix.num_columns):
            tick_manager = self._create_tick_manager_for_column(col_idx)
            self._tick_managers.append(tick_manager)

    def _create_tick_manager_for_column(
        self, column_index: int
    ) -> Optional[Union[NumericTicks, CategoricalTicks]]:
        """
        Create appropriate ticks for a specific column.

        Parameters
        ----------
        column_index : int
            Index of the column to create ticks for.

        Returns
        -------
        Union[NumericTicks, CategoricalTicks] or None
            The created ticks, or None if column is empty.
        """
        column_type = self._matrix.get_column_type(column_index)

        if column_type == ColumnType.NUMERIC:
            numeric_column = self._matrix.get_numeric_column(column_index)

            # Generate ticks if data exists and min != max
            if (
                numeric_column.effective_min_val is not None
                and numeric_column.effective_min_val
                != numeric_column.effective_max_val
            ):
                tick_manager = NumericTicks.from_range(
                    min_val=numeric_column.effective_min_val,
                    max_val=numeric_column.effective_max_val,
                    axis_data=numeric_column,
                )
                return tick_manager
            else:
                # Create ticks without tick values for single values
                tick_manager = NumericTicks(axis_data=numeric_column)
                return tick_manager

        elif column_type == ColumnType.CATEGORICAL:
            categorical_column = self._matrix.get_categorical_column(
                column_index
            )

            # Only create ticks if categories exist
            if categorical_column.categories:
                tick_manager = CategoricalTicks.from_categories(
                    categories=categorical_column.categories,
                    axis_data=categorical_column,
                )
                return tick_manager
            else:
                # No categories, return None
                return None

        # Unknown column type, return None
        return None

    def get_tick_manager(
        self, column_index: int
    ) -> Optional[Union[NumericTicks, CategoricalTicks]]:
        """
        Get the ticks for a specific column.

        Parameters
        ----------
        column_index : int
            Index of the column.

        Returns
        -------
        Union[NumericTicks, CategoricalTicks] or None
            The ticks for the column, or None if not available.
        """
        if 0 <= column_index < len(self._tick_managers):
            return self._tick_managers[column_index]
        return None

    def get_numeric_tick_manager(
        self, column_index: int
    ) -> NumericTicks:
        """
        Get ticks as NumericTicks. Raises TypeError if not numeric.

        Parameters
        ----------
        column_index : int
            Index of the column.

        Returns
        -------
        NumericTicks
            The numeric ticks for the column.

        Raises
        ------
        TypeError
            If the column is not numeric.
        """
        tick_manager = self.get_tick_manager(column_index)
        if not isinstance(tick_manager, NumericTicks):
            raise TypeError(f"Column {column_index} is not numeric.")
        return tick_manager

    def get_categorical_tick_manager(
        self, column_index: int
    ) -> CategoricalTicks:
        """
        Get ticks as CategoricalTicks. Raises TypeError if not categorical.

        Parameters
        ----------
        column_index : int
            Index of the column.

        Returns
        -------
        CategoricalTicks
            The categorical ticks for the column.

        Raises
        ------
        TypeError
            If the column is not categorical.
        """
        tick_manager = self.get_tick_manager(column_index)
        if not isinstance(tick_manager, CategoricalTicks):
            raise TypeError(f"Column {column_index} is not categorical.")
        return tick_manager
