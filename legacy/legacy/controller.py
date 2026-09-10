"""
Controller module for paxplot library.

This module provides the main interface for users to interact with the paxplot
library. The PaxController class handles data management, plotting operations,
and visualization customization in a clean, intuitive API.
"""

from typing import (
    Sequence, Union, List, Optional, Tuple, Dict, Any
)
import numpy as np
from numpy.typing import NDArray
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from .plot_model import PlotModel
from .matplotlib_integration.matplotlib_renderer import MatplotlibRenderer


class PaxController:
    """
    Main controller class for paxplot library.
    
    This is the primary interface that users interact with to create, manage,
    and customize parallel coordinate plots. The controller provides a clean,
    intuitive API that follows matplotlib patterns.
    
    Examples
    --------
    Basic usage:
        >>> controller = PaxController()
        >>> controller.plot(data)
        >>> controller.set_column_names(['A', 'B', 'C'])
        >>> controller.show()
    
    Method chaining:
        >>> controller = PaxController()
        >>> controller.plot(data).set_column_names(['X', 'Y', 'Z']).show()
    """
    
    def __init__(self):
        """Initialize the PaxController."""
        self._plot_model: Optional[PlotModel] = None
        self._renderer: Optional[MatplotlibRenderer] = None
        self._plot_created = False
    
    @property
    def num_rows(self) -> int:
        """Number of rows in the current dataset."""
        if self._plot_model is None:
            return 0
        return self._plot_model.num_rows
    
    @property
    def num_columns(self) -> int:
        """Number of columns in the current dataset."""
        if self._plot_model is None:
            return 0
        return self._plot_model.num_columns
    
    @property
    def column_names(self) -> Optional[List[str]]:
        """Current column names, if set."""
        if self._plot_model is None or self._plot_model._named_view is None:
            return None
        return self._plot_model._named_view.column_names
    
    def plot(
        self, 
        data: Optional[Sequence[Sequence[Union[str, int, float]]]] = None,
        figsize: Optional[Tuple[float, float]] = None,
        **kwargs
    ) -> 'PaxController':
        """
        Create and display the parallel coordinate plot.
        
        Parameters
        ----------
        data : Sequence[Sequence[Union[str, int, float]]], optional
            Data to plot. If None, uses existing data.
        figsize : Tuple[float, float], optional
            Figure size (width, height) in inches.
        **kwargs
            Additional arguments passed to the renderer.
            
        Returns
        -------
        PaxController
            Self for method chaining.
            
        Raises
        ------
        ValueError
            If no data is available to plot.
        """
        # Handle data input
        if data is not None:
            if not data:
                raise ValueError("Data cannot be empty")
            
            # Create or replace plot model
            self._plot_model = PlotModel(data)
            self._plot_created = False
        
        # Check if we have data to plot
        if self._plot_model is None or self.num_rows == 0:
            raise ValueError("No data available to plot")
        
        # Create renderer if needed
        if self._renderer is None or not self._plot_created:
            self._renderer = MatplotlibRenderer(
                self._plot_model, 
                figsize=figsize,
                **kwargs
            )
            self._plot_created = True
        
        # Update the plot
        self._renderer.update()
        
        return self
    
    def show(self) -> None:
        """
        Display the plot.
        
        This follows matplotlib's pattern where show() is called separately
        to display the plot.
        """
        if self._renderer is None:
            raise RuntimeError("No plot created yet. Call plot() first.")
        
        self._renderer.show()
    
    def add_data(
        self, 
        data: Sequence[Sequence[Union[str, int, float]]],
        append: bool = False
    ) -> 'PaxController':
        """
        Add data to the plot.
        
        Parameters
        ----------
        data : Sequence[Sequence[Union[str, int, float]]]
            Data to add. Each inner sequence represents a row of data points.
        append : bool, default=False
            If True, append to existing data. If False, replace existing data.
            
        Returns
        -------
        PaxController
            Self for method chaining.
        """
        if not data:
            raise ValueError("Data cannot be empty")
        
        if not append or self._plot_model is None:
            # Replace existing data or create new plot model
            self._plot_model = PlotModel(data)
            self._plot_created = False
        else:
            # Append to existing data
            for row in data:
                if self._plot_model is not None:
                    self._plot_model.append_rows([row])
            self._plot_created = False
        
        return self
    
    def add_row(self, row: Sequence[Union[str, int, float]]) -> 'PaxController':
        """
        Add a single row of data.
        
        Parameters
        ----------
        row : Sequence[Union[str, int, float]]
            Single row of data to add.
            
        Returns
        -------
        PaxController
            Self for method chaining.
        """
        if self.num_columns > 0 and len(row) != self.num_columns:
            raise ValueError(
                f"Row length ({len(row)}) must match existing column count "
                f"({self.num_columns})"
            )
        
        if self._plot_model is not None:
            self._plot_model.append_rows([row])
            self._plot_created = False
        
        return self
    
    def remove_row(self, row_index: int) -> 'PaxController':
        """
        Remove a row from the dataset.
        
        Parameters
        ----------
        row_index : int
            Index of the row to remove.
            
        Returns
        -------
        PaxController
            Self for method chaining.
        """
        if row_index < 0 or row_index >= self.num_rows:
            raise IndexError(f"Row index {row_index} out of bounds")
        
        if self._plot_model is not None:
            self._plot_model.remove_rows([row_index])
            self._plot_created = False
        
        return self
    
    def set_column_names(self, names: List[str]) -> 'PaxController':
        """
        Set names for the columns.
        
        Parameters
        ----------
        names : List[str]
            Column names. Must match the number of columns in the data.
            
        Returns
        -------
        PaxController
            Self for method chaining.
        """
        if len(names) != self.num_columns:
            raise ValueError(
                f"Number of names ({len(names)}) must match column count "
                f"({self.num_columns})"
            )
        
        if self._plot_model is not None:
            self._plot_model.set_column_names(names)
        
        return self
    
    def get_column_data(
        self, 
        column: Union[int, str], 
        normalized: bool = False
    ) -> NDArray[np.float64] | List[Union[str, int, float]]:
        """
        Get data for a specific column.
        
        Parameters
        ----------
        column : Union[int, str]
            Column index or name.
        normalized : bool, default=False
            If True, return normalized values. If False, return raw values.
            
        Returns
        -------
        NDArray[np.float64] | List[Union[str, int, float]]
            Column data as normalized array or raw values list.
        """
        if self._plot_model is None:
            raise ValueError("No data available")
        
        if isinstance(column, str):
            if self.column_names is None:
                raise ValueError("Column names not set")
            try:
                column_idx = self.column_names.index(column)
            except ValueError:
                raise ValueError(f"Column name '{column}' not found")
        else:
            column_idx = column
        
        if normalized:
            return self._plot_model.get_column_values_normalized(column_idx)
        else:
            return self._plot_model.get_column_values(column_idx)
    
    def set_custom_bounds(
        self, 
        column: Union[int, str], 
        min_val: Optional[float] = None, 
        max_val: Optional[float] = None
    ) -> 'PaxController':
        """
        Set custom bounds for a numeric column.
        
        Parameters
        ----------
        column : Union[int, str]
            Column index or name.
        min_val : float, optional
            Custom minimum value for normalization.
        max_val : float, optional
            Custom maximum value for normalization.
            
        Returns
        -------
        PaxController
            Self for method chaining.
        """
        if self._plot_model is None:
            raise ValueError("No data available")
        
        if isinstance(column, str):
            if self.column_names is None:
                raise ValueError("Column names not set")
            try:
                column_idx = self.column_names.index(column)
            except ValueError:
                raise ValueError(f"Column name '{column}' not found")
        else:
            column_idx = column
        
        self._plot_model.set_column_custom_bounds(column_idx, min_val, max_val)
        self._plot_created = False
        
        return self
    
    def get_custom_bounds(
        self, 
        column: Union[int, str]
    ) -> Tuple[Optional[float], Optional[float]]:
        """
        Get custom bounds for a column.
        
        Parameters
        ----------
        column : Union[int, str]
            Column index or name.
            
        Returns
        -------
        Tuple[Optional[float], Optional[float]]
            (min_value, max_value) tuple.
        """
        if self._plot_model is None:
            raise ValueError("No data available")
        
        if isinstance(column, str):
            if self.column_names is None:
                raise ValueError("Column names not set")
            try:
                column_idx = self.column_names.index(column)
            except ValueError:
                raise ValueError(f"Column name '{column}' not found")
        else:
            column_idx = column
        
        min_val = self._plot_model.get_column_custom_min(column_idx)
        max_val = self._plot_model.get_column_custom_max(column_idx)
        return min_val, max_val
    
    def clear_custom_bounds(self, column: Union[int, str]) -> 'PaxController':
        """
        Clear custom bounds for a column, reverting to auto-scaling.
        
        Parameters
        ----------
        column : Union[int, str]
            Column index or name.
            
        Returns
        -------
        PaxController
            Self for method chaining.
        """
        return self.set_custom_bounds(column, None, None)
    
    def save_plot(
        self, 
        filename: str, 
        dpi: int = 300, 
        bbox_inches: str = 'tight',
        **kwargs
    ) -> None:
        """
        Save the current plot to a file.
        
        Parameters
        ----------
        filename : str
            Output filename with extension (e.g., 'plot.png', 'plot.pdf').
        dpi : int, default=300
            Resolution in dots per inch.
        bbox_inches : str, default='tight'
            Bounding box setting for the saved figure.
        **kwargs
            Additional arguments passed to figure.savefig().
        """
        if self._renderer is None:
            raise RuntimeError("No plot created yet. Call plot() first.")
        
        figure = self._renderer.figure
        figure.savefig(
            filename, 
            dpi=dpi, 
            bbox_inches=bbox_inches,
            **kwargs
        )
    
    def clear_data(self) -> 'PaxController':
        """
        Clear all data from the plot.
        
        Returns
        -------
        PaxController
            Self for method chaining.
        """
        self._plot_model = None
        self._plot_created = False
        self._renderer = None
        return self

    
    def __repr__(self) -> str:
        """String representation of the controller."""
        return (
            f"PaxController(rows={self.num_rows}, "
            f"columns={self.num_columns}, "
            f"plot_created={self._plot_created})"
        )
    
    def __str__(self) -> str:
        """User-friendly string representation."""
        if self.num_rows == 0:
            return "PaxController: No data"
        
        return (
            f"PaxController: {self.num_rows} rows, {self.num_columns} columns"
            f"{f', columns: {self.column_names}' if self.column_names else ''}"
        )