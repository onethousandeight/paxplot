"""
Numeric Ticks for PaxPlot

This module provides the NumericTicks class which handles the creation,
normalization, and management of numeric tick marks for plot axes.

The NumericTicks maintains tick values synchronized with axis data bounds, 
ensuring ticks are properly normalized to the [-1, 1] internal coordinate system
used by PaxPlot. It provides methods for:

- Generating evenly-spaced, "nice" tick marks using matplotlib's locator algorithms
- Setting custom tick values
- Adding individual tick marks
- Retrieving both raw and normalized tick values
- Automatic updates when axis bounds change

The manager acts as an observer to its associated axis data, automatically
adjusting its normalization parameters when the axis data changes to maintain
visual consistency between data and tick marks.
"""

from typing import Optional, Sequence, Union, List
import matplotlib.ticker as mticker
from paxplot.legacy.data_managers.numeric_normalized_array import NumericNormalizedArray


class NumericTicks:
    """
    Manages numeric axis ticks normalized to [-1, 1],
    storing ticks only inside the internal NumericNormalizedArray.
    """

    def __init__(
            self,
            axis_data: NumericNormalizedArray,
            tick_values: Optional[Sequence[Union[int, float]]] = None
        ):
        """
        Initialize with a sequence of numeric tick values.

        Parameters
        ----------
        tick_values : Sequence[Union[int, float]]
            Initial tick values.
        """
        if tick_values is None:
            tick_values = [0.0]
        self._ticks = NumericNormalizedArray(values=tick_values)

        self._axis_data = axis_data
        self._set_tick_bounds_equal_to_axis_bounds()
        self._axis_data.register_observer(self._on_axis_data_normalization_recomputed)

    @classmethod
    def _compute_ticks(
        cls,
        min_val: float,
        max_val: float,
        max_ticks: int = 10,
        integer: bool = False,
    ) -> List[float]:
        """
        Internal helper to compute nice ticks using matplotlib logic.

        Parameters
        ----------
        min_val : float
            Minimum axis value.
        max_val : float
            Maximum axis value.
        max_ticks : int
            Maximum number of ticks to generate.
        integer : bool
            Generate integer ticks only if True.

        Returns
        -------
        List[float]
            List of computed ticks within [min_val, max_val].
        """
        if min_val >= max_val:
            raise ValueError("min_val must be less than max_val")

        locator = mticker.MaxNLocator(nbins=max_ticks, integer=integer, prune=None)
        ticks = locator.tick_values(min_val, max_val)
        return [t for t in ticks if min_val <= t <= max_val]

    @classmethod
    def from_range(
        cls,
        min_val: float,
        max_val: float,
        axis_data: NumericNormalizedArray,
        max_ticks: int = 10,
        integer: bool = False,
    ) -> "NumericTicks":
        """
        Create an instance by generating "nice" ticks in [min_val, max_val]
        using matplotlib logic and associating it with an axis_data
        NumericNormalizedArray.

        Parameters
        ----------
        min_val : float
            Minimum value of the axis range.
        max_val : float
            Maximum value of the axis range.
        axis_data : NumericNormalizedArray
            Existing axis data object to link for normalization tracking.
        max_ticks : int, optional
            Maximum number of ticks to generate (default 10).
        integer : bool, optional
            Whether to generate integer ticks only (default False).

        Returns
        -------
        NumericTicks
            New instance initialized with generated ticks and axis data.
        """
        ticks = cls._compute_ticks(min_val, max_val, max_ticks=max_ticks, integer=integer)
        return cls(axis_data=axis_data, tick_values=ticks)

    def generate_ticks(
        self,
        min_val: float,
        max_val: float,
        max_ticks: int = 10,
        integer: bool = False,
    ) -> None:
        """
        Generate "nice" tick values within [min_val, max_val] using matplotlib logic,
        then set those ticks internally.

        Parameters
        ----------
        min_val : float
            Minimum axis value.
        max_val : float
            Maximum axis value.
        max_ticks : int, optional
            Maximum number of ticks to generate (default 10).
        integer : bool, optional
            If True, generate integer ticks only (default False).
        """
        ticks = self._compute_ticks(min_val, max_val, max_ticks=max_ticks, integer=integer)
        self.set_ticks(ticks)

    def set_ticks(self, tick_values: Sequence[Union[int, float]]) -> None:
        """
        Replace current ticks with a new sequence.

        Parameters
        ----------
        tick_values : Sequence[Union[int, float]]
            New tick values.
        """
        self._ticks.update_array(tick_values)

    def add_tick(self, tick_value: Union[int, float]) -> None:
        """
        Add a single numeric tick value.

        Parameters
        ----------
        tick_value : Union[int, float]
            Tick value to add.
        """
        self._ticks.append_array([tick_value])

    def get_raw_values(self) -> List[Union[int, float]]:
        """
        Get the raw tick values stored in the normalized array.

        Returns
        -------
        List[Union[int, float]]
            Raw tick values.
        """
        return list(self._ticks.values)

    def get_normalized_values(self) -> List[float]:
        """
        Get normalized tick values in [-1, 1].

        Returns
        -------
        List[float]
            Normalized tick values.
        """
        return self._ticks.values_normalized.tolist()

    def _on_axis_data_normalization_recomputed(self) -> None:
        """
        Observer callback invoked when the linked axis_data's normalization
        parameters are recomputed.

        This method ensures that the tick bounds remain synchronized with the
        current effective min/max values of the associated axis data by calling
        `_set_tick_bounds_equal_to_axis_bounds()`.
        """
        self._set_tick_bounds_equal_to_axis_bounds()

    def _set_tick_bounds_equal_to_axis_bounds(self) -> None:
        """
        Update the ticks' normalization bounds to match the linked
        axis_data's normalization bounds.

        If `self._axis_data` is set, this method overrides the internal
        NumericNormalizedArray's normalization bounds so that tick values are
        normalized relative to the same range as the axis data. This ensures
        consistent scaling between axis labels and plotted data.
        """
        if self._axis_data is not None:
            self._ticks.set_custom_bounds(
                min_val=self._axis_data.effective_min_val,
                max_val=self._axis_data.effective_max_val
            )
