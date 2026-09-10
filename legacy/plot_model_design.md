# HighDimensionalPlotModel Design Document

## Overview

The `HighDimensionalPlotModel` class serves as the main interface for creating and managing plot structures in PaxPlot. It coordinates values management through an ArrayManager and automatically creates associated structures including TickManager, AxisLabels, and CustomAxisLimits.

## Core Concept

Every time values are modified (initialization, append, or remove operations), the HighDimensionalPlotModel automatically updates all associated structures to maintain consistency across the plot components.

## Class Design

```python
class HighDimensionalPlotModel:
    """
    Main interface for creating and managing plot structures.

    The HighDimensionalPlotModel serves as the primary interface for users to interact with
    PaxPlot values. It manages an ArrayManager for values storage and automatically
    creates and maintains associated structures including TickManager,
    AxisLabels, and CustomAxisLimits.

    Parameters
    ----------
    values : Sequence[Sequence[Union[str, int, float]]], optional
        Initial values as a 2D sequence where each row is a sequence of values
        and each column should be consistently typed. If None, creates an
        empty model that can be populated later.

    Attributes
    ----------
    array_manager : ArrayManager
        The underlying array manager managing all columns of values.
    tick_manager : TickManager
        Manager for tick collections corresponding to each column.
    axis_labels : List[AxisLabel]
        List of axis labels, one for each column (initially None).
    custom_limits : List[CustomAxisLimit]
        List of custom axis limits, one for each column (initially None).

    """

    def __init__(
        self, values: Optional[Sequence[Sequence[Union[str, int, float]]]] = None
    ) -> None:
        """
        Initialize HighDimensionalPlotModel with optional initial values.

        Parameters
        ----------
        values : Sequence[Sequence[Union[str, int, float]]], optional
            Initial values as a 2D sequence. If None, creates an empty model.

        Raises
        ------
        ValueError
            If the values structure is invalid (empty or inconsistent row lengths).
        """
        # Initialize with empty structures first, then use set_values method
        self._array_manager = ArrayManager([])
        self._tick_manager = TickManager([])
        self._axis_labels = []
        self._custom_limits = []
        
        if values is not None:
            self.set_values(values)

    @property
    def array_manager(self) -> ArrayManager:
        """
        Get the underlying array manager.

        Returns
        -------
        ArrayManager
            The array manager containing all values columns.
        """

    @property
    def tick_manager(self) -> TickManager:
        """
        Get the tick manager for all columns.

        Returns
        -------
        TickManager
            The tick manager containing tick collections for each column.
        """

    @property
    def axis_labels(self) -> List[AxisLabel]:
        """
        Get the list of axis labels.

        Returns
        -------
        List[AxisLabel]
            List of axis labels, one for each column. Initially all labels are None.
        """

    @property
    def custom_limits(self) -> List[CustomAxisLimit]:
        """
        Get the list of custom axis limits.

        Returns
        -------
        List[CustomAxisLimit]
            List of custom axis limits, one for each column. Initially all limits are None.
        """

    def append_values(self, row: Sequence[Union[str, int, float]]) -> None:
        """
        Append a new row of values to the array manager and update all structures.

        This method adds a new row to the underlying array manager and automatically
        updates the tick manager, axis labels, and custom limits to maintain
        consistency. The tick manager will regenerate ticks based on the
        updated values.

        Parameters
        ----------
        row : Sequence[Union[str, int, float]]
            The row of values to append. Must have the same length as existing columns.

        Raises
        ------
        ValueError
            If the row length doesn't match the number of columns.
        """

    def remove_values(self, indices: Sequence[int]) -> None:
        """
        Remove rows at the specified indices and update all structures.

        This method removes the specified rows from the underlying array manager
        and automatically updates the tick manager, axis labels, and custom
        limits to maintain consistency. The tick manager will regenerate
        ticks based on the updated values.

        Parameters
        ----------
        indices : Sequence[int]
            The indices of rows to remove.

        Raises
        ------
        IndexError
            If any index is out of bounds.
        ValueError
            If indices are not valid integers.
        """

    def set_values(self, values: Sequence[Sequence[Union[str, int, float]]]) -> None:
        """
        Set new values for the plot model, replacing all existing values and updating all structures.

        This method replaces all existing values in the underlying array manager
        and automatically updates the tick manager, axis labels, and custom
        limits to maintain consistency. The tick manager will regenerate
        ticks based on the new values, and all associated structures will
        be reset to their initial state.

        Parameters
        ----------
        values : Sequence[Sequence[Union[str, int, float]]]
            The new values as a 2D sequence where each row is a sequence
            of values and each column should be consistently typed.

        Raises
        ------
        ValueError
            If the values structure is invalid (empty or inconsistent row lengths).
        """


    def set_axis_label(self, index: int, label: str) -> None:
        """
        Set the axis label for a specific column.

        Parameters
        ----------
        index : int
            The index of the column to set the label for.
        label : str
            The label text to set.

        Raises
        ------
        IndexError
            If the index is out of bounds.
        ValueError
            If the label is empty or invalid.
        """

    def clear_axis_label(self, index: int) -> None:
        """
        Clear the axis label for a specific column.

        Parameters
        ----------
        index : int
            The index of the column to clear the label for.

        Raises
        ------
        IndexError
            If the index is out of bounds.
        """

    def set_custom_limit(
        self, 
        index: int, 
        min_val: Optional[float] = None, 
        max_val: Optional[float] = None
    ) -> None:
        """
        Set custom axis limits for a specific column.

        Parameters
        ----------
        index : int
            The index of the column to set limits for.
        min_val : float, optional
            Custom minimum value for the axis.
        max_val : float, optional
            Custom maximum value for the axis.

        Raises
        ------
        IndexError
            If the index is out of bounds.
        TypeError
            If min_val or max_val are not numeric or None.
        ValueError
            If both min_val and max_val are set and min_val >= max_val.
        """

    def clear_custom_limit(self, index: int) -> None:
        """
        Clear custom axis limits for a specific column.

        Parameters
        ----------
        index : int
            The index of the column to clear limits for.

        Raises
        ------
        IndexError
            If the index is out of bounds.
        """

    def __repr__(self) -> str:
        """
        Get a string representation of the plot model.

        Returns
        -------
        str
            A string representation showing the model dimensions and structure counts.
        """
```

## Key Design Principles

1. **Automatic Structure Management**: Every values modification triggers updates to all associated structures
2. **Type Safety**: Full type hints and proper error handling
3. **Consistency**: Maintains consistency between ArrayManager, TickManager, AxisLabels, and CustomAxisLimits
4. **User-Friendly Interface**: Simple methods like `append()` and `remove()` for values manipulation
5. **Extensibility**: Designed to be easily extended with new features

## Usage Pattern

```python
# Create model with values
plot_model = HighDimensionalPlotModel(values)

# Modify values
plot_model.append_values(more_values)
plot_model.remove_values(indices)
plot_model.set_values(new_values)  # Replace all values

# Access structures (automatically maintained)
array_manager = plot_model.array_manager  # Direct access to underlying ArrayManager
ticks = plot_model.tick_manager
labels = plot_model.axis_labels
limits = plot_model.custom_limits
```

## Implementation Notes

- The underlying values management happens through the ArrayManager class
- Initialization follows the established pattern: create empty structures first, then use `set_values()` method
- Every time values are modified, the HighDimensionalPlotModel calls internal methods to update:
  - TickManager (regenerates ticks based on current values)
  - AxisLabels (maintains list structure)
  - CustomAxisLimits (maintains list structure)
- All structures are initially created as empty and populated as needed
- The `set_values()` method provides a consistent interface for both initialization and values replacement
