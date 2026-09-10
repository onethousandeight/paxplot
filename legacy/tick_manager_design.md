# TickManager Design Document

## Overview

The `TickManager` class provides a unified interface for managing collections of tick objects (`NumericTicks` and `CategoricalTicks`). Similar to how the `Matrix` class manages collections of arrays, the `TickManager` manages collections of tick objects, ensuring consistency and providing convenient access methods.

## Design Principles

- **Unified Management**: Single interface for managing multiple tick collections
- **Type Safety**: Strong typing with proper validation and error handling
- **Consistency**: Ensures all managed tick collections follow the same patterns
- **Flexibility**: Supports both numeric and categorical tick types
- **Extensibility**: Designed to accommodate future tick types and features

## Class Structure

### TickManager

```python
class TickManager:
    """
    A manager for collections of tick objects.
    
    This class provides a unified interface for managing multiple tick collections,
    where each collection can be either NumericTicks or CategoricalTicks.
    The manager ensures consistency across tick collections and provides
    convenient access methods.
    
    Parameters
    ----------
    tick_types : Sequence[TickType]
        The types of tick collections to create and manage.
    
    Attributes
    ----------
    tick_collections : List[Union[NumericTicks, CategoricalTicks]]
        The stored tick collections.
    num_collections : int
        The number of tick collections managed.
    
    Examples
    --------
    >>> # Initialize with tick types
    >>> manager = TickManager([
    ...     TickType.NUMERIC,
    ...     TickType.CATEGORICAL
    ... ])
    >>> print(manager.num_collections)  # 2
    >>> 
    >>> # Get and configure tick collections
    >>> numeric_ticks = manager.get_numeric_ticks(0)
    >>> numeric_ticks.set_ticks_from_range(0, 100)
    >>> 
    >>> categorical_ticks = manager.get_categorical_ticks(1)
    >>> categorical_ticks.set_ticks_from_categories(['A', 'B', 'C'])
    >>> 
    >>> print(manager.get_tick_collection(0).labels.values)  # ['0.0', '25.0', ...]
    """
```

### TickType Enum

```python
class TickType(str, Enum):
    """Represents the type of a tick collection in the manager.
    
    Parameters
    ----------
    NUMERIC : str
        Collection contains NumericTicks.
    CATEGORICAL : str
        Collection contains CategoricalTicks.
    """
    
    NUMERIC = "numeric"
    CATEGORICAL = "categorical"
```

## Core Methods

### Collection Management

```python
def remove_tick_collection(self, index: int) -> None:
    """Remove a tick collection at the specified index.
    
    Parameters
    ----------
    index : int
        The index of the collection to remove.
    
    Raises
    ------
    IndexError
        If the index is out of bounds.
    """

def get_tick_collection(self, index: int) -> Union[NumericTicks, CategoricalTicks]:
    """Get a tick collection at the specified index.
    
    Parameters
    ----------
    index : int
        The index of the collection to get.
    
    Returns
    -------
    Union[NumericTicks, CategoricalTicks]
        The tick collection at the specified index.
    
    Raises
    ------
    IndexError
        If the index is out of bounds.
    """
```

### Type-Specific Access

```python
def get_numeric_ticks(self, index: int) -> NumericTicks:
    """Get a NumericTicks collection at the specified index.
    
    Parameters
    ----------
    index : int
        The index of the collection to get.
    
    Returns
    -------
    NumericTicks
        The NumericTicks collection at the specified index.
    
    Raises
    ------
    IndexError
        If the index is out of bounds.
    TypeError
        If the collection at the specified index is not NumericTicks.
    """

def get_categorical_ticks(self, index: int) -> CategoricalTicks:
    """Get a CategoricalTicks collection at the specified index.
    
    Parameters
    ----------
    index : int
        The index of the collection to get.
    
    Returns
    -------
    CategoricalTicks
        The CategoricalTicks collection at the specified index.
    
    Raises
    ------
    IndexError
        If the index is out of bounds.
    TypeError
        If the collection at the specified index is not CategoricalTicks.
    """

def get_tick_type(self, index: int) -> TickType:
    """Get the type of a tick collection at the specified index.
    
    Parameters
    ----------
    index : int
        The index of the collection to get.
    
    Returns
    -------
    TickType
        The type of the tick collection.
    
    Raises
    ------
    IndexError
        If the index is out of bounds.
    """
```



### Magic Methods

```python
def __len__(self) -> int:
    """Get the number of tick collections.
    
    Returns
    -------
    int
        The number of tick collections.
    """

def __getitem__(self, index: int) -> Union[NumericTicks, CategoricalTicks]:
    """Get a tick collection at the specified index.
    
    Parameters
    ----------
    index : int
        The index of the collection to get.
    
    Returns
    -------
    Union[NumericTicks, CategoricalTicks]
        The tick collection at the specified index.
    """

def __repr__(self) -> str:
    """Get a string representation of the tick manager.
    
    Returns
    -------
    str
        A string representation showing the number of collections and their types.
    """
```

## Properties

```python
@property
def tick_collections(self) -> List[Union[NumericTicks, CategoricalTicks]]:
    """Get the tick collections as a list.
    
    Returns
    -------
    List[Union[NumericTicks, CategoricalTicks]]
        A copy of the tick collections list.
    """

@property
def num_collections(self) -> int:
    """Get the number of tick collections.
    
    Returns
    -------
    int
        The number of tick collections.
    """
```

## Validation and Error Handling

- **Type Validation**: Ensures only valid tick types are provided during initialization
- **Index Validation**: Validates all index parameters
- **Consistency Checks**: Validates tick collection integrity
- **Direct Access**: Users modify tick collections directly through the returned objects

## Usage Examples

### Basic Usage

```python
# Create manager with tick types
manager = TickManager([
    TickType.NUMERIC,
    TickType.CATEGORICAL
])

# Configure numeric ticks
numeric_ticks = manager.get_numeric_ticks(0)
numeric_ticks.set_ticks_from_range(0, 100, max_ticks=5)

# Configure categorical ticks
categorical_ticks = manager.get_categorical_ticks(1)
categorical_ticks.set_ticks_from_categories(['Low', 'Medium', 'High'])

# Access collections
print(manager.num_collections)  # 2
print(manager.get_tick_type(0))  # TickType.NUMERIC
print(manager.get_tick_type(1))  # TickType.CATEGORICAL
```

### Advanced Usage

```python
# Modify specific collections directly
numeric_ticks = manager.get_numeric_ticks(0)
numeric_ticks.append(['125.0'], [125.0])

categorical_ticks = manager.get_categorical_ticks(1)
categorical_ticks.remove([0])  # Remove first tick

# Access individual tick data
print(numeric_ticks.labels.values)     # ['0.0', '25.0', '50.0', '75.0', '100.0', '125.0']
print(categorical_ticks.locations.values)  # [1, 2] (after removing first tick)
```

## Implementation Notes

1. **Initialization**: Creates empty tick objects based on provided types during `__init__`
2. **Storage**: Uses a private list `_tick_collections` to store tick objects
3. **Validation**: Leverages existing validation from `BaseTicks` classes
4. **Type Safety**: Uses proper type hints and runtime type checking
5. **Error Handling**: Follows the same error handling patterns as `Matrix`
6. **Documentation**: Uses NumPy-style docstrings for consistency

### Initialization Process

The `TickManager` initialization follows this process:

1. **Type Validation**: Validates that all provided types are valid `TickType` values
2. **Object Creation**: Creates empty tick objects based on the types:
   - `TickType.NUMERIC` → `NumericTicks()`
   - `TickType.CATEGORICAL` → `CategoricalTicks()`
3. **Storage**: Stores the created objects in `_tick_collections`
4. **Ready State**: Manager is immediately ready for use with `get_numeric_ticks()` and `get_categorical_ticks()` methods

## Testing Strategy

- Unit tests for all public methods
- Validation tests for error conditions
- Integration tests with existing tick classes
- Performance tests for large collections
- Type safety tests for mixed tick types

## Future Extensions

- Support for tick collection metadata (names, descriptions)
- Batch operations across multiple collections
- Tick collection filtering and searching
- Integration with plotting systems
- Serialization/deserialization support
