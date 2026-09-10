"""Categorical ticks for handling categorical tick marks."""

from typing import List, Optional, Sequence
from paxplot.legacy.data_managers.categorical_normalized_array import CategoricalNormalizedArray


class CategoricalTicks:
    """
    Manages categorical axis ticks normalized to [-1, 1],
    storing ticks inside the internal CategoricalNormalizedArray.
    """

    def __init__(
            self,
            axis_data: CategoricalNormalizedArray,
            tick_values: Optional[Sequence[str]] = None
        ):
        """
        Initialize with a sequence of categorical tick values.

        Parameters
        ----------
        axis_data : CategoricalNormalizedArray
            The axis data array to link for normalization tracking.
        tick_values : Sequence[str], optional
            Initial tick values. If None, an empty list will be used.
        """
        if tick_values is None:
            tick_values = []
        self._ticks = CategoricalNormalizedArray(values=tick_values)

        self._axis_data = axis_data
        # Register to be notified when axis data changes
        self._axis_data.register_observer(self._on_axis_data_normalization_recomputed)

    @classmethod
    def from_categories(
        cls,
        categories: Sequence[str],
        axis_data: CategoricalNormalizedArray
    ) -> "CategoricalTicks":
        """
        Create an instance with ticks based on all provided categories,
        associated with an axis_data CategoricalNormalizedArray.

        Parameters
        ----------
        categories : Sequence[str]
            Categories to use as tick values.
        axis_data : CategoricalNormalizedArray
            Existing axis data object to link for normalization tracking.

        Returns
        -------
        CategoricalTicks
            New instance initialized with all category ticks and axis data.
        """
        return cls(axis_data=axis_data, tick_values=list(categories))

    def set_ticks(self, tick_values: Sequence[str]) -> None:
        """
        Replace current ticks with a new sequence.

        Parameters
        ----------
        tick_values : Sequence[str]
            New tick values.
        """
        self._ticks.update_array(tick_values)

    def get_raw_values(self) -> List[str]:
        """
        Get the raw tick values stored in the normalized array.

        Returns
        -------
        List[str]
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
        
        For categorical data, this ensures that any changes in the axis data's
        label-to-index mapping are properly reflected in the tick positions.
        """
        self._update_ticks_to_match_axis_data()

    def _update_ticks_to_match_axis_data(self) -> None:
        """Update ticks to match the axis data's categories.
        """
        self.set_ticks(self._axis_data.categories)
