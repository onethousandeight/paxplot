# PaxPlot Architecture Design Document

## Overview

This document outlines the refactored architecture for PaxPlot, a parallel coordinate plotting library. The new design separates data management from normalization and rendering concerns, creating a more flexible and maintainable system.

## Core Principles

1. **Separation of Concerns**: Data structures are independent of normalization and rendering
2. **Pull-Based Updates**: Data views pull fresh data when needed
3. **View Pattern**: Normalization provided through lightweight data views
4. **Renderer Agnostic**: Core system works with any rendering backend

## Architecture Components

### Directory Structure

```
src/paxplot/
├── __init__.py
├── structures/
│   ├── __init__.py
│   ├── arrays/
│   │   ├── __init__.py
│   │   ├── base_array.py
│   │   ├── numerical_array.py
│   │   └── categorical_array.py
│   ├── matrix.py
│   ├── tick_manger.py
│   ├── limits/
│   │   ├── __init__.py
│   │   └── custom_axis_limit.py
│   ├── labels/
│   │   ├── __init__.py
│   │   └── axis_label.py
│   └── ticks/
│       ├── __init__.py
│       ├── base_ticks.py
│       ├── numeric_ticks.py
│       └── categorical_ticks.py
├── models/
│   ├── __init__.py
│   └── plot_model.py
├── renderers/
│   ├── __init__.py
│   ├── base_renderer.py
│   ├── matplotlib_renderer.py
│   └── render_data.py
├── legacy/
└── datasets.py
```

### Core Data Structures

#### `NumericalArray`
Stores numerical data as an array with basic operations and NaN handling.

```python
class NumericalArray(BaseArray[float]):
    """Array for storing numerical data with validation and NaN handling."""
    
    def __init__(self, values: Sequence[Union[float, int]]):
        """Initialize with numerical values."""
        pass
    
    def append(self, values: Sequence[Union[float, int]]) -> None:
        """Append numerical values to the array."""
        pass
    
    def remove(self, indices: Sequence[int]) -> None:
        """Remove values at specified indices."""
        pass
    
    @property
    def values(self) -> List[float]:
        """Get the stored numerical values."""
        pass
    
    @property
    def min(self) -> float:
        """Get the minimum value."""
        pass
    
    @property
    def max(self) -> float:
        """Get the maximum value."""
        pass
```

#### `CategoricalArray`
Stores categorical (string) data as an array with unique value tracking.

```python
class CategoricalArray(BaseArray[str]):
    """Array for storing categorical data with unique value tracking."""
    
    def __init__(self, values: Sequence[str]):
        """Initialize with categorical values."""
        pass
    
    def append(self, values: Sequence[str]) -> None:
        """Append categorical values to the array."""
        pass
    
    def remove(self, indices: Sequence[int]) -> None:
        """Remove values at specified indices."""
        pass
    
    @property
    def values(self) -> List[str]:
        """Get the stored categorical values."""
        pass
    
    @property
    def unique_values(self) -> List[str]:
        """Get unique values in the array."""
        pass
```

#### `Matrix`
Manages collections of arrays, providing a unified interface for data management.

```python
class Matrix:
    """Matrix for managing collections of numerical and categorical arrays."""
    
    def __init__(self, data: Sequence[Sequence[Union[str, int, float]]]):
        """Initialize matrix with 2D data."""
        pass
    
    @property
    def columns(self) -> List[Union[NumericalArray, CategoricalArray]]:
        """Get the columns as a list of arrays."""
        pass
    
    @property
    def num_columns(self) -> int:
        """Get the number of columns."""
        pass
    
    @property
    def num_rows(self) -> int:
        """Get the number of rows."""
        pass
    
    def append_data(self, row: Sequence[Union[str, int, float]]) -> None:
        """Append a row of data."""
        pass
    
    def remove_data(self, indices: Sequence[int]) -> None:
        """Remove rows at specified indices."""
        pass
    
    def get_numeric_array(self, index: int) -> NumericalArray:
        """Get numerical array at index, raises error if not numerical."""
        pass
    
    def get_categorical_array(self, index: int) -> CategoricalArray:
        """Get categorical array at index, raises error if not categorical."""
        pass
```

### Tick Management

#### `BaseTicks`
Base tick information containing positions and labels.

```python
class BaseTicks(ABC):
    """Abstract base class for tick management."""
    
    def __init__(self, labels: Sequence[str], locations: Sequence[Union[float, int]]):
        """Initialize with labels and locations."""
        pass
    
    @property
    def labels(self) -> CategoricalArray:
        """Get the tick labels."""
        pass
    
    @property
    def locations(self) -> NumericalArray:
        """Get the tick positions."""
        pass
    
    @property
    def positions(self) -> List[float]:
        """Get tick positions as a list."""
        pass
```

#### `NumericTicks`
Manages numeric tick generation and customization.

```python
class NumericTicks(BaseTicks):
    """Tick management for numerical data."""
    
    def __init__(self, array: NumericalArray):
        """Initialize with numerical array."""
        pass
    
    def generate_ticks(self, num_ticks: int = 5) -> 'NumericTicks':
        """Generate evenly spaced ticks."""
        pass
    
    def set_custom_ticks(self, tick_values: List[float]) -> 'NumericTicks':
        """Set custom tick values."""
        pass
```

#### `CategoricalTicks`
Manages categorical tick generation and customization.

```python
class CategoricalTicks(BaseTicks):
    """Tick management for categorical data."""
    
    def __init__(self, array: CategoricalArray):
        """Initialize with categorical array."""
        pass
    
    def generate_ticks(self) -> 'CategoricalTicks':
        """Generate ticks for all unique values."""
        pass
    
    def set_custom_ticks(self, tick_labels: List[str]) -> 'CategoricalTicks':
        """Set custom tick labels."""
        pass
```

#### `TickManager`
Coordinates tick management across all columns.

```python
class TickManager:
    """Manager for tick collections across all columns."""
    
    def __init__(self, matrix: Matrix):
        """Initialize with matrix."""
        pass
    
    def get_ticks(self, column_index: int) -> BaseTicks:
        """Get ticks for a specific column."""
        pass
    
    def get_numeric_ticks(self, column_index: int) -> NumericTicks:
        """Get numeric ticks for a column."""
        pass
    
    def get_categorical_ticks(self, column_index: int) -> CategoricalTicks:
        """Get categorical ticks for a column."""
        pass
```

### Additional Structures

#### `AxisLabel`
Manages axis label text and styling.

```python
class AxisLabel:
    """Axis label with text and optional styling."""
    
    def __init__(self, text: str):
        """Initialize with label text."""
        pass
    
    @property
    def text(self) -> str:
        """Get the label text."""
        pass
    
    def set_text(self, text: str) -> None:
        """Set the label text."""
        pass
```

#### `CustomAxisLimit`
Manages custom axis limits for display.

```python
class CustomAxisLimit:
    """Custom axis limits for display configuration."""
    
    def __init__(self, min_val: Optional[float] = None, max_val: Optional[float] = None):
        """Initialize with optional min/max values."""
        pass
    
    @property
    def min_val(self) -> Optional[float]:
        """Get the minimum value."""
        pass
    
    @property
    def max_val(self) -> Optional[float]:
        """Get the maximum value."""
        pass
    
    def set_limits(self, min_val: Optional[float], max_val: Optional[float]) -> None:
        """Set custom limits."""
        pass
```

### Plot Model

#### `HighDimensionalPlotModel`
User-friendly interface that coordinates all components.

```python
class HighDimensionalPlotModel:
    """Main interface for creating and managing plot structures."""
    
    def __init__(self, data: Optional[Sequence[Sequence[Union[str, int, float]]]] = None):
        """Initialize with optional data."""
        pass
    
    @property
    def matrix(self) -> Matrix:
        """Get the underlying data matrix."""
        pass
    
    @property
    def tick_manager(self) -> TickManager:
        """Get the tick manager."""
        pass
    
    @property
    def axis_labels(self) -> List[AxisLabel]:
        """Get the list of axis labels."""
        pass
    
    @property
    def custom_limits(self) -> List[CustomAxisLimit]:
        """Get the list of custom axis limits."""
        pass
    
    def append_data(self, row: Sequence[Union[str, int, float]]) -> None:
        """Append a row of data."""
        pass
    
    def remove_data(self, indices: Sequence[int]) -> None:
        """Remove rows at specified indices."""
        pass
    
    def set_axis_label(self, index: int, label: str) -> None:
        """Set axis label for a column."""
        pass
    
    def set_custom_limit(self, index: int, min_val: Optional[float] = None, 
                        max_val: Optional[float] = None) -> None:
        """Set custom axis limits for a column."""
        pass
```

## Normalization Strategy

Normalization logic is embedded directly in the render data classes. This approach provides:

1. **Simplicity**: No additional abstraction layers
2. **Performance**: Direct computation without extra object creation
3. **Clarity**: All rendering logic in one place
4. **Flexibility**: Each renderer can implement its own normalization strategy

The normalization happens during render data creation, converting raw data to the format needed for rendering.

## Renderer System

### Base Renderer Interface

```python
class BaseRenderer(ABC):
    """Abstract base class for all renderers."""
        
    @abstractmethod
    def render(self, render_data: Any) -> Any:
        """Render a figure from render data.
        
        Parameters
        ----------
        render_data : Any
            Renderer-specific data containing all information needed for rendering.
            
        Returns
        -------
        Any
            The rendered figure/plot object.
        """
        pass
```

### Render Data Classes

Each renderer defines its own immutable data contract:

```python
@dataclass(frozen=True)
class MatplotlibRenderData:
    """Immutable data snapshot for matplotlib rendering.
    
    Contains all data needed to render a matplotlib figure, including
    normalized values, tick information, axis labels, and styling options.
    This data is a snapshot at a point in time and does not stay in sync
    with the original plot model.
    
    Attributes
    ----------
    normalized_values : List[NDArray[float]]
        Normalized data values for each column.
    tick_positions : List[List[float]]
        Tick positions for each column.
    tick_labels : List[List[str]]
        Tick labels for each column.
    axis_labels : List[str]
        Axis labels for each column.
    figure_size : Tuple[float, float]
        Figure size in inches (width, height).
    customizations : Dict[str, Any]
        Rendering customizations (colors, linewidth, etc.).
    """
    normalized_values: List[NDArray[float]]
    tick_positions: List[List[float]]
    tick_labels: List[List[str]]
    axis_labels: List[str]
    figure_size: Tuple[float, float]
    customizations: Dict[str, Any]
    
    @classmethod
    def from_plot_model(cls, plot_model: HighDimensionalPlotModel, 
                       customizations: Dict[str, Any] = None) -> 'MatplotlibRenderData':
        """Create render data from plot model with embedded normalization.
        
        Parameters
        ----------
        plot_model : HighDimensionalPlotModel
            The plot model containing data and structures.
        customizations : Dict[str, Any], optional
            Rendering customizations to apply.
            
        Returns
        -------
        MatplotlibRenderData
            Immutable data snapshot for matplotlib rendering.
            
        Notes
        -----
        Normalization logic is embedded in this method. Numerical data is
        normalized to 0-1 range using min-max scaling. Categorical data is
        mapped to evenly spaced positions in the 0-1 range.
        """
        pass

@dataclass(frozen=True)
class PlotlyRenderData:
    """Immutable data snapshot for plotly rendering.
    
    Contains all data needed to render a plotly figure, including
    normalized values, tick information, and plotly-specific configuration.
    
    Attributes
    ----------
    normalized_values : List[NDArray[float]]
        Normalized data values for each column.
    tick_positions : List[List[float]]
        Tick positions for each column.
    tick_labels : List[List[str]]
        Tick labels for each column.
    axis_labels : List[str]
        Axis labels for each column.
    trace_config : Dict[str, Any]
        Plotly trace configuration options.
    layout_config : Dict[str, Any]
        Plotly layout configuration options.
    """
    normalized_values: List[NDArray[float]]
    tick_positions: List[List[float]]
    tick_labels: List[List[str]]
    axis_labels: List[str]
    trace_config: Dict[str, Any]
    layout_config: Dict[str, Any]
    
    @classmethod
    def from_plot_model(cls, plot_model: HighDimensionalPlotModel, 
                       customizations: Dict[str, Any] = None) -> 'PlotlyRenderData':
        """Create render data from plot model with embedded normalization.
        
        Parameters
        ----------
        plot_model : HighDimensionalPlotModel
            The plot model containing data and structures.
        customizations : Dict[str, Any], optional
            Rendering customizations to apply.
            
        Returns
        -------
        PlotlyRenderData
            Immutable data snapshot for plotly rendering.
            
        Notes
        -----
        Normalization logic is embedded in this method. Each renderer can
        implement its own normalization strategy as needed.
        """
        pass
```

### Matplotlib Renderer

```python
class MatplotlibRenderer(BaseRenderer):
    """Renders static matplotlib figures from render data.
    
    This renderer creates matplotlib figures that do not stay in sync with
    the original data. Users must call render() again to get updated figures
    when the underlying data changes.
    """
    
    def render(self, render_data: MatplotlibRenderData) -> Figure:
        """Render a static matplotlib figure from render data.
        
        Creates a matplotlib figure using the provided render data. The
        figure is a static snapshot and will not update if the original
        data changes.
        
        Parameters
        ----------
        render_data : MatplotlibRenderData
            Immutable data snapshot containing all rendering information.
            
        Returns
        -------
        Figure
            The rendered matplotlib figure.
        """
        pass
```

### Plotly Renderer

```python
class PlotlyRenderer(BaseRenderer):
    """Renders static plotly figures from render data.
    
    This renderer creates plotly figures that do not stay in sync with
    the original data. Users must call render() again to get updated figures
    when the underlying data changes.
    """
    
    def render(self, render_data: PlotlyRenderData) -> 'plotly.graph_objects.Figure':
        """Render a static plotly figure from render data.
        
        Creates a plotly figure using the provided render data. The
        figure is a static snapshot and will not update if the original
        data changes.
        
        Parameters
        ----------
        render_data : PlotlyRenderData
            Immutable data snapshot containing all rendering information.
            
        Returns
        -------
        plotly.graph_objects.Figure
            The rendered plotly figure.
        """
        pass
```

## Main Interface

### `PaxPlot`

The main user interface that coordinates everything:

```python
class PaxPlot:
    """Main interface for creating and rendering parallel coordinate plots.
    
    This class provides a high-level interface for creating parallel coordinate
    plots with multiple renderers. It manages data through a PlotModel and
    coordinates rendering through various renderer backends.
    
    Attributes
    ----------
    _plot_model : Optional[HighDimensionalPlotModel]
        The underlying plot model containing data and structures.
    _renderers : Dict[str, BaseRenderer]
        Dictionary of registered renderers by name.
    _customizations : Dict[str, Any]
        Global customization settings applied to all renderers.
    """
    
    def __init__(self):
        """Initialize the PaxPlot interface."""
        pass
    
    def plot(self, data: Sequence[Sequence[Union[str, int, float]]]) -> 'PaxPlot':
        """Set up plot data.
        
        Parameters
        ----------
        data : Sequence[Sequence[Union[str, int, float]]]
            The data to plot as a 2D sequence.
            
        Returns
        -------
        PaxPlot
            Self for method chaining.
        """
        pass
    
    def remove_data(self, indices: Sequence[int]) -> 'PaxPlot':
        """Remove rows from the plot data.
        
        Parameters
        ----------
        indices : Sequence[int]
            The indices of rows to remove.
            
        Returns
        -------
        PaxPlot
            Self for method chaining.
        """
        pass
    
    def append_data(self, row: Sequence[Union[str, int, float]]) -> 'PaxPlot':
        """Append a row to the plot data.
        
        Parameters
        ----------
        row : Sequence[Union[str, int, float]]
            The row of data to append.
            
        Returns
        -------
        PaxPlot
            Self for method chaining.
        """
        pass
    
    def add_renderer(self, name: str, renderer: BaseRenderer) -> 'PaxPlot':
        """Add a renderer.
        
        Parameters
        ----------
        name : str
            Name to register the renderer under.
        renderer : BaseRenderer
            The renderer to add.
            
        Returns
        -------
        PaxPlot
            Self for method chaining.
        """
        pass
    
    def set_color(self, color: str) -> 'PaxPlot':
        """Customize plot color.
        
        Parameters
        ----------
        color : str
            Color to use for plot lines.
            
        Returns
        -------
        PaxPlot
            Self for method chaining.
        """
        pass
    
    def set_linewidth(self, width: float) -> 'PaxPlot':
        """Customize line width.
        
        Parameters
        ----------
        width : float
            Width of plot lines.
            
        Returns
        -------
        PaxPlot
            Self for method chaining.
        """
        pass
    
    def set_figsize(self, size: Tuple[float, float]) -> 'PaxPlot':
        """Customize figure size.
        
        Parameters
        ----------
        size : Tuple[float, float]
            Figure size as (width, height) in inches.
            
        Returns
        -------
        PaxPlot
            Self for method chaining.
        """
        pass
    
    def set_axis_label(self, column: int, label: str) -> 'PaxPlot':
        """Set axis label for a column.
        
        Parameters
        ----------
        column : int
            The column index to set the label for.
        label : str
            The label text.
            
        Returns
        -------
        PaxPlot
            Self for method chaining.
        """
        pass
    
    def set_custom_ticks(self, column: int, ticks: List[Union[float, str]]) -> 'PaxPlot':
        """Set custom ticks for a column.
        
        Parameters
        ----------
        column : int
            The column index to set ticks for.
        ticks : List[Union[float, str]]
            The custom tick values.
            
        Returns
        -------
        PaxPlot
            Self for method chaining.
        """
        pass
    
    def show(self) -> Dict[str, Any]:
        """Render and display all plots.
        
        Creates render data from the current plot model and renders
        using all registered renderers. Returns a dictionary of
        rendered figures keyed by renderer name.
        
        Returns
        -------
        Dict[str, Any]
            Dictionary of rendered figures by renderer name.
            
        Raises
        ------
        ValueError
            If no data has been set via plot().
        """
        pass
```

## Usage Examples

### Basic Usage

```python
# Initialize, plot, customize, show
plot = PaxPlot()
plot.plot(data)
plot.show()  # Renders with fresh normalization
```

### Multiple Renderers

```python
# Create plot with multiple renderers
plot = PaxPlot()
plot.add_renderer('matplotlib', MatplotlibRenderer())
plot.add_renderer('plotly', PlotlyRenderer())

# All renderers show when show() is called
plot.plot(data)
plot.show()  # Both matplotlib and plotly render
```

### Customization

```python
# Customize before showing
plot = PaxPlot()
plot.plot(data)
plot.set_color('red')
plot.set_linewidth(2.0)
plot.set_figsize((12, 8))
plot.set_axis_label(0, 'Temperature')
plot.show()  # Renders with all customizations
```

### Data Modification

```python
# Modify data and re-render
plot = PaxPlot()
plot.plot(data)
plot.show()  # Initial render

# Add more data
plot.append_data([4, 'D', 2.5])
plot.show()  # Re-render with updated data

# Remove some data
plot.remove_data([0, 2])
plot.show()  # Re-render with modified data
```

### Static Rendering

```python
# Figures are static snapshots
plot = PaxPlot()
plot.plot(data)
figures = plot.show()  # Returns dict of figures

# Data changes don't affect existing figures
plot.append_data([5, 'E', 3.0])
# figures['matplotlib'] is still the old figure

# Must call show() again to get updated figures
new_figures = plot.show()  # Fresh figures with new data
```

## Benefits

1. **Separation of Concerns**: Data structures, normalization views, and renderers are independent
2. **Static Rendering**: Figures are snapshots that don't stay in sync - users control when to re-render
3. **Renderer Agnostic**: Easy to add new rendering backends with their own data contracts
4. **Immutable Data**: Render data is immutable, preventing accidental modifications
5. **Clear Contracts**: Each renderer defines exactly what data it needs
6. **Simple Architecture**: No complex caching, observers, or notification systems
7. **Maintainability**: Clear boundaries between components with well-defined interfaces
8. **Testability**: Each component can be tested independently with mock data
9. **Extensibility**: Easy to add new features without affecting existing code
10. **Memory Efficient**: No observer or caching overhead, data computed on-demand
11. **Industry Standard**: Similar to matplotlib's static rendering approach
12. **Easy to Understand**: Straightforward data flow from plot model to render data to figures

## Migration Strategy

1. **Core Data Structures** ✅ (Already implemented)
   - `NumericalArray`, `CategoricalArray`, `Matrix`
   - `TickManager`, `CustomAxisLimit`, `AxisLabel`

2. **Plot Model** (Next)
   - `HighDimensionalPlotModel` class coordinating all structures
   - Automatic structure updates on data changes

3. **Renderer System** (Next)
   - `BaseRenderer` interface
   - `MatplotlibRenderData` and `MatplotlibRenderer`
   - `PlotlyRenderData` and `PlotlyRenderer` (future)

4. **Main Interface** (Next)
   - `PaxPlot` class with method chaining
   - Integration with existing structures and new renderers

5. **Testing and Documentation** (Final)
   - Unit tests for all components
   - Integration tests for full workflow
   - Update examples and documentation

This architecture provides a solid foundation for PaxPlot's future development while maintaining clean separation between data management and rendering concerns. The design uses embedded normalization logic for simplicity and aligns with the existing implemented structures, providing a clear path forward for the remaining components.
