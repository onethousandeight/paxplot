# Axis Tick Implementation Plan

## Overview
This document outlines the plan for implementing the tick management system in the `structures/ticks` folder. The system will provide a flexible and extensible way to manage axis ticks and labels for PaxPlot.

## Architecture

### Core Components
1. **BaseTicks** - Abstract base class providing common tick functionality
2. **NumericTicks** - Concrete implementation for numerical axis ticks using matplotlib's MaxNLocator
3. **CategoricalTicks** - Concrete implementation for categorical axis ticks using category indices

## Class Design

### BaseTicks (Abstract Base Class)

#### Purpose
- Provide a common interface for all tick types
- Manage the relationship between tick labels and locations
- Ensure consistency across different tick implementations

#### Core Properties
- `.labels` - CategoricalArray containing tick label text
- `.locations` - NumericalArray containing tick positions on the axis

#### Key Methods
- `__init__(labels, locations)` - Initialize with labels and locations
- `validate()` - Ensure labels and locations arrays have matching lengths
- `add_ticks(labels, locations)` - Add multiple ticks with validation, returns success boolean
- `remove_ticks(indices)` - Remove ticks at specified indices, returns success boolean

#### Validation Rules
- Labels and locations arrays must have the same length
- Labels cannot be empty strings
- Locations must be finite numbers (no NaN or inf)
- When adding ticks: validate new labels aren't empty and locations aren't infinite
- When removing ticks: ensure indices are valid and arrays stay in sync

### NumericTicks (Concrete Implementation)

#### Purpose
- Generate optimal numerical ticks between min and max values using matplotlib's MaxNLocator
- Allow users to specify the maximum number of ticks (default: 5)
- Leverage matplotlib's proven tick generation algorithms for optimal spacing and readability

#### Constructor Parameters
- `max_ticks: int = 5` - Maximum number of ticks to generate (default: 5)

#### Key Methods
- `generate_ticks_from_range(min_value, max_value, max_ticks=5, precision=2)` - Generate ticks from min/max using MaxNLocator

#### Tick Generation Logic
- Use matplotlib's `MaxNLocator` as the internal engine for tick generation
- MaxNLocator automatically determines optimal tick positions and spacing
- Respects the maximum number of ticks constraint while choosing "nice" numbers
- Use `add_ticks()` method to populate the arrays with MaxNLocator results
- Support precision parameter for rounding of the labels
- Handle edge cases (single tick, very small ranges) through MaxNLocator's robust algorithms

#### MaxNLocator Integration
- Create MaxNLocator instance with `nbins=max_ticks`
- Use `MaxNLocator.tick_values(min_value, max_value)` to get optimal tick positions
- Convert tick positions to string labels with specified precision
- MaxNLocator handles automatic selection of "nice" numbers (e.g., 0, 25, 50, 75, 100 instead of 0, 20, 40, 60, 80, 100)

### CategoricalTicks (Concrete Implementation)

#### Purpose
- Generate categorical ticks from a sequence of category strings
- Map category labels to their corresponding indices for positioning
- Provide a bridge between categorical data and numerical positioning on axes

#### Constructor Parameters
- No parameters - creates empty ticks initially

#### Key Methods
- `generate_ticks_from_categories(categories: Sequence[str])` - Generate ticks from category strings

#### Tick Generation Logic
- Accept a sequence of category strings (e.g., ['A', 'B', 'C', 'D'])
- Store categories in the `.labels` CategoricalArray
- Use CategoricalArray's `get_category_indices()` method to get numerical positions
- Store the resulting indices in the `.locations` NumericalArray
- Categories are positioned at their index values (0, 1, 2, 3, ...)
- Maintains order for consistent positioning

#### CategoricalArray Integration
- Leverage CategoricalArray's built-in category management
- Use `get_category_indices()` to convert category strings to numerical positions
- Categories are automatically deduplicated and ordered by CategoricalArray
- Index positions correspond to the order of categories in the array
- Users access categories and indices directly through `.labels` and `.locations` properties

#### Example Flow
```python
# Input categories
categories = ['Red', 'Blue', 'Green', 'Yellow']

# After generate_ticks_from_categories(categories):
# .labels.values = ['Red', 'Blue', 'Green', 'Yellow']
# .locations.values = [0, 1, 2, 3]

# Category 'Blue' is positioned at index 1
# Category 'Yellow' is positioned at index 3
```

## Implementation Details

### File Structure
```
src/paxplot/structures/ticks/
├── __init__.py          # Module exports
├── base_ticks.py        # BaseTicks abstract class
├── numeric_ticks.py     # NumericTicks implementation
└── categorical_ticks.py # CategoricalTicks implementation
```

### Dependencies
- `CategoricalArray` from `structures.arrays.categorical_array`
- `NumericalArray` from `structures.arrays.numerical_array`
- `matplotlib.ticker.MaxNLocator` for NumericTicks tick generation engine
- Standard library: `abc`, `typing`, `math`, `collections.abc`

### Type Hints
- Use proper type hints throughout
- Generic types where appropriate
- Union types for flexible input parameters

### Error Handling
- Validate input parameters in constructors
- Raise descriptive ValueError for invalid inputs
- Ensure arrays remain in sync (same length)
- Handle MaxNLocator edge cases gracefully

### Performance Considerations
- Lazy evaluation of tick calculations
- Cache computed tick positions and labels
- Efficient array operations using existing array classes
- MaxNLocator provides optimized tick generation algorithms

## Usage Examples

### Basic NumericTicks
```python
# Create ticks with default max_ticks=5
ticks = NumericTicks()
ticks.generate_ticks_from_range(0, 100)
print(ticks.labels.values)  # ['0.0', '25.0', '50.0', '75.0', '100.0']
print(ticks.locations.values)  # [0.0, 25.0, 50.0, 75.0, 100.0]

# Create ticks with custom max_ticks
ticks = NumericTicks(max_ticks=3)
ticks.generate_ticks_from_range(0, 100)
print(ticks.labels.values)  # ['0.0', '50.0', '100.0']
```

### Regenerating Ticks
```python
ticks = NumericTicks(max_ticks=5)
ticks.generate_ticks_from_range(0, 10)  # Generate up to 5 ticks from 0 to 10
ticks.generate_ticks_from_range(0, 20)  # Regenerate with up to 5 ticks from 0 to 20

# Change max_ticks and regenerate
ticks.generate_ticks_from_range(0, 20, max_ticks=3)  # Now generates up to 3 ticks
```

### MaxNLocator Benefits
```python
# MaxNLocator chooses "nice" numbers automatically
ticks = NumericTicks(max_ticks=6)
ticks.generate_ticks_from_range(0, 100)
# Results in: [0.0, 20.0, 40.0, 60.0, 80.0, 100.0] (nice spacing)

# Compare with manual spacing - MaxNLocator is smarter about number selection
```

### Basic CategoricalTicks
```python
# Create categorical ticks from category strings
ticks = CategoricalTicks()
categories = ['Red', 'Blue', 'Green', 'Yellow']
ticks.generate_ticks_from_categories(categories)
print(ticks.labels.values)     # ['Red', 'Blue', 'Green', 'Yellow']
print(ticks.locations.values)  # [0, 1, 2, 3]

# Access underlying arrays directly for lookups
blue_index = ticks.locations.values[ticks.labels.values.index('Blue')]  # 1
green_category = ticks.labels.values[2]  # 'Green'
```

### Updating Categories
```python
ticks = CategoricalTicks()
ticks.generate_ticks_from_categories(['A', 'B', 'C'])
# .labels = ['A', 'B', 'C'], .locations = [0, 1, 2]

ticks.generate_ticks_from_categories(['X', 'Y', 'Z', 'W'])
# .labels = ['X', 'Y', 'Z', 'W'], .locations = [0, 1, 2, 3]
```

### CategoricalArray Benefits
```python
# CategoricalArray handles deduplication and ordering automatically
ticks = CategoricalTicks()
categories = ['Blue', 'Red', 'Blue', 'Green', 'Red']
ticks.generate_ticks_from_categories(categories)
# Results in: .labels = ['Blue', 'Red', 'Green'], .locations = [0, 1, 2]
# Duplicates removed, order preserved from first occurrence
```

## Testing Strategy

### Unit Tests
- Test BaseTicks validation and core functionality
- Test NumericTicks tick generation with various ranges and max_ticks values
- Test MaxNLocator integration and edge cases
- Test CategoricalTicks generation from various category sequences
- Test CategoricalArray integration and index mapping
- Test error conditions and validation
- Test that MaxNLocator produces reasonable tick positions
- Test direct access to underlying arrays

### Integration Tests
- Verify compatibility with existing array classes
- Test tick updates and modifications
- Ensure proper error propagation
- Test MaxNLocator behavior with extreme ranges
- Test CategoricalTicks with duplicate categories and edge cases


## Implementation Order

1. **Phase 1**: Implement BaseTicks abstract class
   - Define interface and core properties
   - Implement validation and basic operations
   - Add comprehensive tests

2. **Phase 2**: Implement NumericTicks class
   - Extend BaseTicks with numerical functionality
   - Integrate matplotlib's MaxNLocator for tick generation
   - Implement max_ticks parameter in generate_ticks_from_range method
   - Test with various numerical ranges and max_ticks values

3. **Phase 3**: Implement CategoricalTicks class
   - Extend BaseTicks with categorical functionality
   - Integrate CategoricalArray for category management
   - Implement category-to-index mapping using get_category_indices()
   - Test with various category sequences and edge cases

## Notes

- Follow existing code style and patterns from the arrays module
- Use NumPy-style docstrings for all public methods
- Implement comprehensive error handling and validation
- Ensure all methods have proper type hints
- Write tests for all public methods and edge cases
- Leverage matplotlib's MaxNLocator for robust, well-tested tick generation
- MaxNLocator provides automatic "nice number" selection and handles edge cases
- CategoricalTicks leverages CategoricalArray's built-in category management and deduplication
- Both implementations maintain the same BaseTicks interface for consistency
