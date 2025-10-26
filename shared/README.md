# Shared Module 🔗

The shared utilities and data models that provide common functionality across all modules in the LinkedIn Blog AI Assistant project.

## 🎯 Overview

This module contains:
- **Common Data Models**: Shared Pydantic models used across modules
- **Enums**: Centralized enumeration definitions
- **Utilities**: Common helper functions and constants
- **Type Definitions**: Shared type hints and aliases

## 📁 Module Structure

```
shared/
├── models.py              # Common data models and enums
└── README.md              # This file
```

## 🚀 Key Features

### Centralized Data Models
- **Single Source of Truth**: All modules reference the same model definitions
- **Consistency**: Ensures data structure consistency across the application
- **Maintainability**: Changes to models are automatically reflected everywhere
- **Type Safety**: Pydantic validation ensures data integrity

### Shared Enums
- **AggregationStrategy**: Multi-file processing strategies
- **Quality Levels**: Blog quality classifications
- **Processing Status**: Workflow state tracking
- **Message Types**: Chat message classifications

## 📊 Data Models

### AggregationStrategy
```python
class AggregationStrategy(str, Enum):
    """Strategy for aggregating multiple files"""
    SYNTHESIS = "synthesis"      # Blend all insights together
    COMPARISON = "comparison"    # Compare/contrast sources
    SEQUENCE = "sequence"        # Sequential narrative
    TIMELINE = "timeline"        # Chronological story
```

**Usage:**
```python
from shared.models import AggregationStrategy

# In ingestion module
strategy = AggregationStrategy.SYNTHESIS

# In blog_generation module
if strategy == AggregationStrategy.SYNTHESIS:
    # Apply synthesis logic
    pass
```

## 🔧 Configuration

### Import Pattern
All modules should import shared models using:
```python
from shared.models import AggregationStrategy, BlogQuality, ProcessingStatus
```

### Model Dependencies
The shared models are designed to be:
- **Lightweight**: Minimal dependencies
- **Compatible**: Work with all module requirements
- **Extensible**: Easy to add new models as needed

## 🎮 Usage

### Basic Import
```python
from shared.models import AggregationStrategy

# Use in ingestion
strategy = AggregationStrategy.SYNTHESIS
result = await multi_processor.process_aggregated(files, strategy)

# Use in blog generation
if strategy == AggregationStrategy.COMPARISON:
    # Generate comparison-style content
    pass
```

### Enum Validation
```python
from shared.models import AggregationStrategy

# Validate input
user_input = "synthesis"
try:
    strategy = AggregationStrategy(user_input)
    print(f"Valid strategy: {strategy}")
except ValueError:
    print("Invalid strategy")
```

### Type Hints
```python
from shared.models import AggregationStrategy
from typing import List

def process_files(files: List[str], strategy: AggregationStrategy) -> str:
    """Process files with specified strategy"""
    return f"Processing {len(files)} files with {strategy.value} strategy"
```

## 🔄 Module Integration

### Ingestion Module
```python
# ingestion/multi_processor.py
from shared.models import AggregationStrategy

class MultiProcessor:
    async def process_aggregated(
        self, 
        file_paths: List[str], 
        strategy: AggregationStrategy
    ) -> AggregatedContent:
        if strategy == AggregationStrategy.SYNTHESIS:
            return await self._synthesize_content(processed_files)
        # ... other strategies
```

### Blog Generation Module
```python
# blog_generation/config.py
from shared.models import AggregationStrategy

class BlogGenerationState(BaseModel):
    aggregation_strategy: Optional[AggregationStrategy] = None
    
    def apply_strategy(self, strategy: AggregationStrategy):
        self.aggregation_strategy = strategy
```

### Chatbot Module
```python
# chatbot/orchestrator.py
from shared.models import AggregationStrategy

class ChatbotOrchestrator:
    async def _handle_multi_file(self, files: List[str], strategy: AggregationStrategy):
        result = await self.multi_processor.process_aggregated(files, strategy)
        return self._format_aggregated_response(result)
```

## 🧪 Testing

### Model Validation Tests
```python
def test_aggregation_strategy():
    # Test valid values
    assert AggregationStrategy.SYNTHESIS == "synthesis"
    assert AggregationStrategy.COMPARISON == "comparison"
    assert AggregationStrategy.SEQUENCE == "sequence"
    assert AggregationStrategy.TIMELINE == "timeline"
    
    # Test string conversion
    assert str(AggregationStrategy.SYNTHESIS) == "synthesis"
    
    # Test enum creation
    strategy = AggregationStrategy("synthesis")
    assert strategy == AggregationStrategy.SYNTHESIS

def test_enum_iteration():
    strategies = list(AggregationStrategy)
    assert len(strategies) == 4
    assert AggregationStrategy.SYNTHESIS in strategies
```

### Integration Tests
```python
def test_cross_module_compatibility():
    from ingestion.multi_processor import MultiProcessor
    from shared.models import AggregationStrategy
    
    # Test that modules can use shared enums
    processor = MultiProcessor()
    strategy = AggregationStrategy.SYNTHESIS
    
    # This should work without import errors
    assert isinstance(strategy, AggregationStrategy)
```

## 🔧 Development Guidelines

### Adding New Models
1. **Define in shared/models.py**:
```python
class NewModel(BaseModel):
    field1: str
    field2: int
    field3: Optional[List[str]] = None
```

2. **Update imports** in modules that need it:
```python
from shared.models import NewModel, AggregationStrategy
```

3. **Add tests** for the new model:
```python
def test_new_model():
    model = NewModel(field1="test", field2=42)
    assert model.field1 == "test"
    assert model.field2 == 42
```

### Adding New Enums
1. **Define in shared/models.py**:
```python
class NewEnum(str, Enum):
    VALUE1 = "value1"
    VALUE2 = "value2"
```

2. **Use consistent naming**:
- Use UPPER_CASE for enum values
- Use descriptive names
- Follow existing patterns

3. **Add documentation**:
```python
class NewEnum(str, Enum):
    """Description of what this enum represents"""
    VALUE1 = "value1"    # Description of value1
    VALUE2 = "value2"    # Description of value2
```

## 🐛 Troubleshooting

### Import Issues
```python
# Check if shared module is in Python path
import sys
print(sys.path)

# Check if shared module exists
import os
print(os.path.exists("shared/models.py"))

# Test import
try:
    from shared.models import AggregationStrategy
    print("Import successful")
except ImportError as e:
    print(f"Import failed: {e}")
```

### Model Validation Errors
```python
from shared.models import AggregationStrategy

# Test enum validation
try:
    strategy = AggregationStrategy("invalid_value")
except ValueError as e:
    print(f"Validation error: {e}")

# List valid values
valid_values = [s.value for s in AggregationStrategy]
print(f"Valid values: {valid_values}")
```

## 📊 Performance

- **Import Time**: <1ms for model imports
- **Memory Usage**: Minimal (enums are lightweight)
- **Validation Speed**: <1ms for enum validation
- **Cross-Module Access**: No performance impact

## 🔮 Future Enhancements

- [ ] **Additional Enums**: More shared enumeration types
- [ ] **Common Utilities**: Shared helper functions
- [ ] **Type Aliases**: Common type definitions
- [ ] **Validation Helpers**: Shared validation functions
- [ ] **Serialization**: Common serialization utilities

## 📚 Dependencies

Minimal dependencies for maximum compatibility:
- **pydantic**: Data validation and serialization
- **typing**: Type hints and annotations
- **enum**: Enumeration support

## 🤝 Contributing

1. **Fork** the repository
2. **Create** feature branch
3. **Add** new models/enums as needed
4. **Update** documentation
5. **Submit** pull request

### Guidelines
- Keep models lightweight and focused
- Ensure backward compatibility
- Add comprehensive documentation
- Include usage examples

## 📄 License

MIT License - see main project LICENSE file.

---

**Built with ❤️ using Pydantic and modern Python type hints**
