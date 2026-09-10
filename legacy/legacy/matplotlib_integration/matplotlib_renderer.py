"""Matplotlib renderer for PlotModel visualization.

This module provides a clean, maintainable matplotlib renderer that follows
industry standards for separation of concerns and error handling.
"""

from typing import Optional, List, Tuple
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib.lines import Line2D
import numpy as np

from paxplot.legacy.plot_model import PlotModel


class MatplotlibRenderer:
    """
    Renders a PlotModel using matplotlib with clean separation of concerns.

    This renderer follows industry standards by:
    - Separating figure management from rendering logic
    - Using clear, descriptive method names
    - Implementing proper error handling
    - Following the single responsibility principle
    - Providing consistent state management
    """

    # Default styling constants
    DEFAULT_FIGSIZE = (10, 6)
    DEFAULT_LINE_COLOR = "blue"
    DEFAULT_LINE_ALPHA = 0.7
    DEFAULT_LINE_WIDTH = 1.0
    DEFAULT_SPINE_COLOR = "black"
    DEFAULT_SPINE_ALPHA = 0.8
    DEFAULT_SPINE_WIDTH = 1.0
    DEFAULT_Y_LIMITS = (-1.1, 1.1)

    def __init__(
        self,
        plot_model: PlotModel,
        figsize: Optional[Tuple[float, float]] = None,
        **kwargs,
    ):
        """
        Initialize the renderer with a plot model.

        Parameters
        ----------
        plot_model : PlotModel
            The plot model to render.
        figsize : Tuple[float, float], optional
            Figure size (width, height) in inches.
        **kwargs
            Additional arguments passed to plt.figure.

        Raises
        ------
        ValueError
            If plot_model is None or invalid.
        """
        if plot_model is None:
            raise ValueError("plot_model cannot be None")

        self.plot_model = plot_model
        self._figure: Optional[Figure] = None
        self._main_axis: Optional[Axes] = None
        self._secondary_axes: List[Axes] = []
        self._line_objects: List[Line2D] = []

        figsize = figsize or self.DEFAULT_FIGSIZE
        self._initialize_figure_structure(figsize, **kwargs)

    def _validate_plot_model(self) -> None:
        """
        Validate that the plot model is in a valid state for rendering.

        Raises
        ------
        ValueError
            If the plot model is not in a valid state.
        """
        if self.plot_model.num_columns == 0:
            raise ValueError("Cannot render plot model with zero columns")

        if self.plot_model.num_rows == 0:
            # This is valid - just means no data to plot
            return

    def _create_figure(self, figsize: Tuple[float, float], **kwargs) -> Figure:
        """
        Create a new matplotlib figure.

        Parameters
        ----------
        figsize : Tuple[float, float]
            Figure size (width, height) in inches.
        **kwargs
            Additional arguments passed to plt.figure.

        Returns
        -------
        Figure
            The created matplotlib figure.
        """
        return plt.figure(figsize=figsize, **kwargs)

    def _create_main_axis(self, figure: Figure) -> Axes:
        """
        Create the main plotting axis.

        Parameters
        ----------
        figure : Figure
            The matplotlib figure to add the axis to.

        Returns
        -------
        Axes
            The main plotting axis.
        """
        # Create main axis that spans the entire plot area
        main_axis = figure.add_axes((0.1, 0.1, 0.8, 0.8))

        # Set appropriate x-limits based on number of columns
        if self.plot_model.num_columns == 1:
            main_axis.set_xlim((-0.5, 0.5))
        else:
            main_axis.set_xlim((0, self.plot_model.num_columns - 1))

        # Set y-limits with padding to prevent line cropping
        main_axis.set_ylim(self.DEFAULT_Y_LIMITS)

        # Hide main axis ticks and spines
        main_axis.set_xticks([])
        main_axis.set_yticks([])
        for spine in main_axis.spines.values():
            spine.set_visible(False)

        return main_axis

    def _create_secondary_axes(self, main_axis: Axes) -> List[Axes]:
        """
        Create secondary axes for each column.

        Parameters
        ----------
        main_axis : Axes
            The main axis to create secondary axes from.

        Returns
        -------
        List[Axes]
            List of secondary axes, one for each column.
        """
        secondary_axes = []
        n_columns = self.plot_model.num_columns

        for i in range(n_columns):
            if n_columns == 1:
                # Single column case - position at center
                secondary_ax = main_axis.secondary_yaxis("right")
            else:
                # Multiple columns - position each at its x-coordinate
                axis_pos = i / (n_columns - 1) if n_columns > 1 else 0.5
                secondary_ax = main_axis.secondary_yaxis(axis_pos)

            secondary_axes.append(secondary_ax)

        return secondary_axes

    def _apply_axis_styling(self, axis: Axes) -> None:
        """
        Apply consistent styling to a secondary axis.

        Parameters
        ----------
        axis : Axes
            The axis to style.
        """
        # Hide most spines, keep only the left spine for the vertical line
        for spine_name in ["top", "bottom", "right"]:
            axis.spines[spine_name].set_visible(False)

        # Style the left spine as the vertical line
        left_spine = axis.spines["left"]
        left_spine.set_visible(True)
        left_spine.set_color(self.DEFAULT_SPINE_COLOR)
        left_spine.set_linewidth(self.DEFAULT_SPINE_WIDTH)
        left_spine.set_alpha(self.DEFAULT_SPINE_ALPHA)

        # Hide x-axis ticks
        axis.set_xticks([])

        # Set y-limits to match main axis
        axis.set_ylim(self.DEFAULT_Y_LIMITS)

    def _initialize_figure_structure(
        self, figsize: Tuple[float, float], **kwargs
    ) -> None:
        """
        Initialize the matplotlib figure and axes structure (without plotting data).

        Parameters
        ----------
        figsize : Tuple[float, float]
            Figure size (width, height) in inches.
        **kwargs
            Additional arguments passed to plt.figure.
        """
        self._validate_plot_model()

        # Create figure and axes
        self._figure = self._create_figure(figsize, **kwargs)
        self._main_axis = self._create_main_axis(self._figure)
        self._secondary_axes = self._create_secondary_axes(self._main_axis)

        # Apply styling to secondary axes
        for axis in self._secondary_axes:
            self._apply_axis_styling(axis)

        # Set rightmost axis to have ticks on the right
        if self._secondary_axes:
            self._secondary_axes[-1].yaxis.tick_right()

    def _clear_existing_plots(self) -> None:
        """Clear all existing line plots from the main axis."""
        if self._main_axis is not None:
            # Remove existing lines from the main axis
            for artist in self._main_axis.get_children():
                if isinstance(artist, Line2D):
                    artist.remove()
        self._line_objects.clear()

    def _plot_data_lines(self) -> None:
        """Plot continuous lines on the main axis."""
        if self.plot_model.num_rows == 0:
            return

        if self._main_axis is None:
            return

        # Get normalized data for plotting
        normalized_data = np.array(
            [
                self.plot_model.get_column_values_normalized(i)
                for i in range(self.plot_model.num_columns)
            ]
        ).T

        # Plot continuous lines across the entire figure
        x_coords = list(range(self.plot_model.num_columns))

        for row_idx in range(self.plot_model.num_rows):
            y_coords = normalized_data[row_idx, :]
            (line,) = self._main_axis.plot(
                x_coords,
                y_coords,
                color=self.DEFAULT_LINE_COLOR,
                alpha=self.DEFAULT_LINE_ALPHA,
                linewidth=self.DEFAULT_LINE_WIDTH,
            )
            self._line_objects.append(line)

    def _update_axis_ticks(self, axis: Axes, column_index: int) -> None:
        """
        Update tick marks and labels for a specific axis.

        Parameters
        ----------
        axis : Axes
            The axis to update ticks for.
        column_index : int
            The column index corresponding to this axis.
        """
        try:
            # Try numeric ticks first
            tick_values = self.plot_model.get_numeric_ticks(column_index)
            tick_positions = self.plot_model.get_numeric_ticks_normalized(
                column_index
            )
        except TypeError:
            # Fall back to categorical ticks
            tick_labels = self.plot_model.get_categorical_ticks(column_index)
            tick_positions = self.plot_model.get_categorical_ticks_normalized(
                column_index
            )
            tick_values = tick_labels

        # Set the ticks and labels
        axis.set_yticks(tick_positions)
        axis.set_yticklabels([str(val) for val in tick_values])

    def _update_all_ticks(self) -> None:
        """Update tick marks and labels for all secondary axes."""
        for i, axis in enumerate(self._secondary_axes):
            self._update_axis_ticks(axis, i)

    def update(self) -> None:
        """
        Update the visualization to reflect the current state of the plot model.

        This method redraws all data and updates ticks based on the current
        plot model state.
        """
        self._clear_existing_plots()
        self._plot_data_lines()
        self._update_all_ticks()

    @property
    def figure(self) -> Figure:
        """
        Get the matplotlib figure.

        Returns
        -------
        Figure
            The matplotlib figure.
        """
        assert self._figure is not None  # Type guard
        return self._figure

    def show(self) -> None:
        """Display the figure."""
        assert self._figure is not None  # Type guard
        self._figure.show()

    def save(self, filename: str, **kwargs) -> None:
        """
        Save the figure to a file.

        Parameters
        ----------
        filename : str
            The filename to save the figure to.
        **kwargs
            Additional arguments passed to figure.savefig.
        """
        assert self._figure is not None  # Type guard
        self._figure.savefig(filename, **kwargs)

    def close(self) -> None:
        """Close the figure and clean up resources."""
        if self._figure is not None:
            plt.close(self._figure)
            self._figure = None
            self._main_axis = None
            self._secondary_axes.clear()
            self._line_objects.clear()

    def __del__(self):
        """Cleanup when the renderer is destroyed."""
        self.close()
