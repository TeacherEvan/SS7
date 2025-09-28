# Development Workflows - SS6 Super Student Game

## Project Setup and Installation

### Initial Setup

```bash
# 1. Install dependencies (creates Play.bat/Play.sh)
python install.py

# 2. Verify installation
python -c "import pygame; print('Pygame installed successfully')"

# 3. Test basic functionality
python SS6.origional.py --test
```

### Development Environment Setup

- **Python 3.6+** (maintain compatibility)
- **VSCode** with Python extensions
- **Git** for version control
- **Pygame 2.0+** (auto-installed via install.py)

## Common Development Tasks

### 1. Adding New Game Levels

**Workflow:**

1. **Examine existing level** (e.g., `levels/alphabet_level.py`)
2. **Create new level class** following constructor pattern
3. **Implement core game loop** with manager integration
4. **Add to level selection menu** in main game
5. **Test on both display modes**

**Template Pattern:**

```python
class NewLevel:
    def __init__(self, width, height, screen, fonts, small_font, target_font,
                 particle_manager, glass_shatter_manager, multi_touch_manager,
                 hud_manager, checkpoint_manager, center_piece_manager,
                 flamethrower_manager, resource_manager, create_explosion_func,
                 display_mode, voice_generator, sound_system, config_manager):

        # Initialize level-specific variables
        self.display_mode = display_mode
        self.resource_manager = resource_manager
        self.voice_generator = voice_generator

        # Get configuration
        self.config = config_manager
        self.level_config = self.config.get('levels.new_level', {})

    def update(self):
        # Main game loop logic
        pass

    def draw(self, screen):
        # Rendering logic with display mode considerations
        pass

    def handle_event(self, event):
        # Event handling with multi-touch support
        pass
```

### 2. Modifying Visual Elements

**Workflow:**

1. **Check display mode** impact
2. **Update ResourceManager** caching if needed
3. **Test scaling** on both DEFAULT and QBOARD
4. **Verify performance** on target hardware

**Pattern:**

```python
# Always check display mode
def get_particle_count(self):
    base_count = self.config.get('particles.base_count', 25)
    if self.display_mode == 'QBOARD':
        return base_count // 2  # Reduce for performance
    return base_count
```

### 3. Adding Audio Content

**Workflow:**

1. **Generate voice files** using voice system
2. **Add sound effects** with fallback patterns
3. **Update sound cache** in ResourceManager
4. **Test audio timing** with visual elements

**Voice Generation:**

```bash
# Generate all sounds (if needed)
python generate_all_sounds.py

# Generate specific voice file
python -c "
from utils.voice_generator import VoiceGenerator
vg = VoiceGenerator()
vg.generate_voice_file('Hello World', 'sounds/test.wav')
"
```

### 4. Configuration Changes

**Workflow:**

1. **Update JSON config** (`config/game_config.json`)
2. **Update legacy compatibility** in `settings.py` if needed
3. **Test configuration loading** and fallbacks
4. **Validate on both display modes**

**Configuration Pattern:**

```python
# Add new configuration
{
    "new_feature": {
        "enabled": true,
        "default_value": 42,
        "qboard_value": 20
    }
}

# Access in code
feature_value = config.get('new_feature.default_value', 42)
if display_mode == 'QBOARD':
    feature_value = config.get('new_feature.qboard_value', feature_value)
```

## Testing Procedures

### Pre-Development Testing

```bash
# Run full test suite
python run_tests.py

# Test specific components
python -m pytest tests/ -v -k "test_specific_function"

# Performance testing
python sound_performance_test.py
python level_sound_integration_test.py
```

### Development Testing

1. **Unit Tests**: Test individual functions and methods
2. **Integration Tests**: Test manager interactions
3. **Display Tests**: Verify both DEFAULT and QBOARD modes
4. **Performance Tests**: Validate frame rates and memory usage

### Manual Testing Checklist

- [ ] Game launches without errors
- [ ] All levels are accessible from menu
- [ ] Visual elements scale properly
- [ ] Audio plays at correct timing
- [ ] Touch input works correctly
- [ ] ESC key navigation functions
- [ ] Level transitions work smoothly
- [ ] Manager state resets properly
- [ ] Performance acceptable on target hardware

## Debugging Workflows

### Common Issues and Solutions

**Import Errors:**

```bash
# Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# Verify file structure
python -c "import os; print(os.listdir('.'))"
```

**Display Issues:**

```python
# Debug display mode detection
from Display_settings import detect_display_type
print(f"Detected display: {detect_display_type()}")
```

**Audio Issues:**

```python
# Test pygame mixer
python -c "
import pygame
pygame.mixer.init()
print(f'Mixer initialized: {pygame.mixer.get_init()}')
"
```

**Performance Issues:**

```python
# Enable debug display
python SS6.origional.py --debug

# Check memory usage
python utils/memory_profiler.py
```

## Code Modification Best Practices

### 1. Following Existing Patterns

- **Use dependency injection** - Accept all managers in constructor
- **Check display mode** - Optimize for both DEFAULT and QBOARD
- **Implement graceful degradation** - Handle missing resources/files
- **Cache resources** - Use ResourceManager for frequently used assets

### 2. Configuration Management

- **Use config system** - Avoid hardcoding values
- **Provide fallbacks** - Always have default values
- **Test config loading** - Verify JSON/YAML parsing

### 3. Error Handling

```python
# Pattern for all file operations
try:
    with open(file_path, 'r') as f:
        data = json.load(f)
except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f"Config error: {e}")
    data = get_default_config()
```

### 4. Testing New Features

```python
# Create focused test
def test_new_feature():
    # Test with mock dependencies
    # Verify expected behavior
    # Test error conditions
    pass
```

## Deployment Considerations

### Pre-Deployment Checklist

- [ ] All tests pass
- [ ] Both display modes tested
- [ ] Configuration files valid
- [ ] No hardcoded paths or values
- [ ] Error handling verified
- [ ] Performance acceptable
- [ ] Audio files generated
- [ ] Dependencies properly specified

### Installation Testing

```bash
# Test clean installation
python install.py
python SS6.origional.py
```

## Version Control Practices

### Commit Guidelines

- **Atomic commits** - One feature or fix per commit
- **Descriptive messages** - Explain what and why
- **Test before committing** - Ensure functionality works
- **Update documentation** - Keep instructions current

### Branch Strategy

- **Main**: Stable, tested code
- **Feature branches**: New development
- **Release branches**: Prepared releases

## Performance Optimization Workflow

### 1. Identify Bottlenecks

```python
# Use built-in profilers
python -m cProfile SS6.origional.py

# Memory profiling
python utils/memory_profiler.py
```

### 2. Optimize Systematically

- **Profile first** - Measure before optimizing
- **Target QBOARD mode** - Often the limiting factor
- **Use caching** - ResourceManager for surfaces/sounds
- **Reduce object creation** - Object pooling for particles

### 3. Validate Improvements

- **Benchmark before/after** - Compare performance metrics
- **Test both modes** - Ensure no regressions
- **Monitor memory usage** - Verify no memory leaks

This workflow ensures consistent, high-quality development while maintaining the project's plug-and-play design philosophy and educational focus.
