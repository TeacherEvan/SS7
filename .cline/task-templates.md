# Task Templates - SS6 Super Student Game

## Common Task Patterns for Cline Agents

### 1. Adding New Game Levels

**Template:**

```markdown
# Add New [LevelType] Level

## Task Overview
Add a new [level_type] level to the SS6 game following the established patterns.

## Implementation Steps
1. **Examine existing level** (study alphabet_level.py or similar)
2. **Create level class** with proper constructor signature
3. **Implement game logic** (update, draw, handle_event methods)
4. **Add to level menu** in main game file
5. **Test both display modes** (DEFAULT and QBOARD)
6. **Add configuration** for level-specific settings

## Code Template
```python
class [LevelType]Level:
    def __init__(self, width, height, screen, fonts, small_font, target_font,
                 particle_manager, glass_shatter_manager, multi_touch_manager,
                 hud_manager, checkpoint_manager, center_piece_manager,
                 flamethrower_manager, resource_manager, create_explosion_func,
                 display_mode, voice_generator, sound_system, config_manager):

        # Store manager references
        self.display_mode = display_mode
        self.resource_manager = resource_manager
        self.voice_generator = voice_generator
        self.config_manager = config_manager
        self.hud_manager = hud_manager

        # Get level configuration
        self.level_config = self.config_manager.get('levels.[level_type]_level', {})

        # Initialize level-specific variables
        self.items = self.level_config.get('items', [])
        self.current_item_index = 0

    def update(self):
        # Update game state
        # Check for item completion
        # Handle level progression
        pass

    def draw(self, screen):
        # Draw game elements with display mode optimization
        if self.display_mode == 'QBOARD':
            # Optimized drawing for touch displays
            pass
        else:
            # Full effects for standard displays
            pass

    def handle_event(self, event):
        # Handle user input (touch/mouse/keyboard)
        pass
```

## Files to Modify

- `levels/[level_type]_level.py` (create new)
- `SS6.origional.py` (add to level menu)
- `config/game_config.json` (add level configuration)
- `settings.py` (add legacy compatibility if needed)

```

### 2. Modifying Visual Elements

**Template:**
```markdown
# Modify Visual Element: [ElementName]

## Task Overview
Update [element_name] visual behavior with display mode optimization.

## Implementation Steps
1. **Locate element code** in relevant level files
2. **Add display mode checks** for optimization
3. **Update ResourceManager** caching if needed
4. **Test scaling** on both display modes
5. **Verify performance** on target hardware

## Code Pattern
```python
def update_[element_name](self):
    # Get display-optimized settings
    particle_count = self.get_optimized_particle_count()
    animation_speed = self.get_display_optimized_speed()

    # Update element with optimized settings
    for i in range(particle_count):
        # Update particle with speed
        pass

def get_optimized_particle_count(self):
    base_count = self.config.get('particles.[element_name]', 25)
    if self.display_mode == 'QBOARD':
        return max(5, base_count // 2)
    return base_count

def get_display_optimized_speed(self):
    base_speed = self.config.get('animation.[element_name]_speed', 1.0)
    if self.display_mode == 'QBOARD':
        return base_speed * 0.7  # Slower for touch interaction
    return base_speed
```

## Files to Examine

- Current level files using the element
- `utils/resource_manager.py` for caching
- `config/game_config.json` for visual settings

```

### 3. Adding Audio Content

**Template:**
```markdown
# Add Audio Content: [ContentType]

## Task Overview
Add [content_type] audio with multi-tier fallback system.

## Implementation Steps
1. **Generate audio files** using voice generation system
2. **Add caching** in ResourceManager
3. **Implement fallback pattern** (ElevenLabs → SAPI → Synthetic)
4. **Test audio timing** with visual elements
5. **Update configuration** for audio settings

## Code Pattern
```python
def play_[content_type]_audio(self, text):
    # Try to play cached audio first
    cache_file = f"sounds/[content_type]_{text}.wav"
    if os.path.exists(cache_file):
        try:
            self.voice_generator.play_cached_voice(cache_file)
            return
        except Exception as e:
            print(f"Cached audio failed: {e}")

    # Generate new audio with fallbacks
    try:
        # Method 1: ElevenLabs API
        temp_file = self.voice_generator.generate_voice_file(text)
        self.voice_generator.play_voice_file(temp_file)
    except Exception as e:
        try:
            # Method 2: Windows SAPI
            self.voice_generator.generate_sapi_voice(text)
            self.voice_generator.play_voice_file(temp_file)
        except Exception as e:
            # Method 3: Synthetic fallback
            print(f"All audio methods failed: {e}")
            self.play_synthetic_fallback(text)
```

## Commands to Run

```bash
# Generate new audio files
python generate_all_sounds.py

# Test specific audio
python -c "
from utils.voice_generator import VoiceGenerator
vg = VoiceGenerator()
vg.generate_voice_file('[test_text]', 'sounds/test.wav')
"
```

## Files to Modify

- `utils/voice_generator.py` (if adding new generation methods)
- `sounds/` directory (new audio files)
- `config/voice_config.json` (API settings)

```

### 4. Configuration Changes

**Template:**
```markdown
# Update Configuration: [ConfigArea]

## Task Overview
Update [config_area] configuration with proper fallbacks and validation.

## Implementation Steps
1. **Update JSON config** with new settings
2. **Add legacy compatibility** in settings.py if needed
3. **Test configuration loading** and fallbacks
4. **Validate on both display modes**
5. **Update documentation** with new settings

## Configuration Pattern
```json
{
    "[config_area]": {
        "[setting_name]": {
            "enabled": true,
            "default_value": 42,
            "qboard_value": 20,
            "description": "Setting description"
        }
    }
}
```

## Code Access Pattern

```python
def get_[config_area]_setting(self):
    # Get display-specific value
    if self.display_mode == 'QBOARD':
        return self.config.get('[config_area].[setting_name].qboard_value', 42)
    else:
        return self.config.get('[config_area].[setting_name].default_value', 42)

def update_[config_area]_config(self, new_settings):
    # Update configuration with validation
    try:
        # Validate new settings
        validated_settings = self.validate_[config_area]_settings(new_settings)

        # Update config file
        self.config_manager.update('[config_area]', validated_settings)

        # Reload configuration
        self.config_manager.reload()

    except Exception as e:
        print(f"Configuration update failed: {e}")
```

## Files to Modify

- `config/game_config.json` (main configuration)
- `settings.py` (legacy compatibility)
- `utils/config_manager.py` (if adding validation)

```

### 5. Bug Fixes

**Template:**
```markdown
# Fix Bug: [BugDescription]

## Task Overview
Fix [bug_description] that affects [affected_functionality].

## Investigation Steps
1. **Reproduce the bug** with minimal test case
2. **Identify root cause** using debugging techniques
3. **Implement fix** following established patterns
4. **Test fix** on both display modes
5. **Verify no regressions** in existing functionality

## Debug Commands
```bash
# Enable debug logging
python SS6.origional.py --debug

# Test specific scenario
python -c "
# Reproduce bug with minimal code
"

# Check system state
python utils/debug_display.py
```

## Fix Implementation Pattern

```python
def original_function(self):
    try:
        # Original logic that had the bug
        pass
    except [SpecificException] as e:
        # Handle the specific bug
        print(f"Bug condition detected: {e}")
        # Apply fix
        return self.fixed_behavior()
    except Exception as e:
        # Handle unexpected errors
        print(f"Unexpected error: {e}")
        return self.safe_default()
```

## Testing Checklist

- [ ] Bug can be reproduced consistently
- [ ] Fix resolves the issue
- [ ] No new bugs introduced
- [ ] Both display modes work correctly
- [ ] Performance not degraded
- [ ] Error handling still works

```

## Files to Examine
- Files mentioned in bug reports
- Related level and utility files
- Configuration and resource files
```

### 6. Performance Optimization

**Template:**

```markdown
# Optimize Performance: [OptimizationTarget]

## Task Overview
Optimize [target_area] for better performance, especially on QBOARD mode.

## Analysis Steps
1. **Profile current performance** to identify bottlenecks
2. **Identify optimization opportunities** (caching, reduced operations, etc.)
3. **Implement optimizations** with display mode considerations
4. **Measure improvement** before/after
5. **Test both display modes** for regressions

## Profiling Commands
```bash
# Profile main game loop
python -m cProfile -s cumulative SS6.origional.py

# Memory profiling
python utils/memory_profiler.py

# Custom performance test
python -c "
import time
start_time = time.time()
# Test code here
end_time = time.time()
print(f'Execution time: {end_time - start_time:.3f}s')
"
```

## Optimization Pattern

```python
class OptimizedComponent:
    def __init__(self, display_mode, config_manager):
        self.display_mode = display_mode
        self.config = config_manager
        self.cache = {}  # Cache for expensive operations

    def expensive_operation(self, input_value):
        # Check cache first
        cache_key = f"{input_value}_{self.display_mode}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        # Optimize based on display mode
        if self.display_mode == 'QBOARD':
            # Use optimized algorithm for touch displays
            result = self.optimized_algorithm(input_value)
        else:
            # Use full algorithm for standard displays
            result = self.full_algorithm(input_value)

        # Cache result
        self.cache[cache_key] = result
        return result

    def optimized_algorithm(self, input_value):
        # Reduced complexity for QBOARD
        return simplified_calculation(input_value)

    def full_algorithm(self, input_value):
        # Full complexity for DEFAULT
        return complex_calculation(input_value)
```

## Files to Examine

- Performance test files
- Resource-intensive level files
- Particle and animation systems

```

### 7. Testing New Features

**Template:**
```markdown
# Test New Feature: [FeatureName]

## Task Overview
Test [feature_name] functionality across all scenarios and display modes.

## Testing Approach
1. **Unit tests** for individual functions
2. **Integration tests** for manager interactions
3. **Display mode tests** for both DEFAULT and QBOARD
4. **Performance tests** for target hardware
5. **Manual testing** with comprehensive checklist

## Test Code Pattern
```python
class Test[FeatureName](unittest.TestCase):
    def setUp(self):
        # Set up test environment with mocks
        self.mocks = get_mock_managers()
        configure_mocks(self.mocks)
        self.feature = [FeatureName](**self.mocks)

    def test_feature_in_default_mode(self):
        # Test with DEFAULT display mode
        self.feature.display_mode = 'DEFAULT'
        result = self.feature.test_function()
        self.assertEqual(result, expected_value)

    def test_feature_in_qboard_mode(self):
        # Test with QBOARD display mode
        self.feature.display_mode = 'QBOARD'
        result = self.feature.test_function()
        self.assertEqual(result, qboard_expected_value)

    def test_feature_error_handling(self):
        # Test error conditions and fallbacks
        with self.assertRaises(ExpectedException):
            self.feature.test_function()

    def test_feature_performance(self):
        # Test performance requirements
        import time
        start_time = time.time()
        self.feature.test_function()
        execution_time = time.time() - start_time
        self.assertLess(execution_time, max_allowed_time)
```

## Test Commands

```bash
# Run specific feature tests
python -m pytest tests/ -v -k "[feature_name]"

# Run performance tests
python sound_performance_test.py
python level_sound_integration_test.py

# Manual testing
python SS6.origional.py --test-mode
```

## Files to Create/Modify

- `tests/test_[feature_name].py` (new test file)
- Existing test files (add new test methods)
- Performance test files (if needed)

```

## Quick Reference Commands

### Development Commands
```bash
# Install and setup
python install.py

# Run game
python SS6.origional.py

# Run tests
python run_tests.py

# Generate sounds
python generate_all_sounds.py

# Debug mode
python SS6.origional.py --debug
```

### File Locations

- **Main entry**: `SS6.origional.py`
- **Level files**: `levels/`
- **Utilities**: `utils/`
- **Configuration**: `config/`
- **Audio files**: `sounds/`
- **Assets**: `assets/`
- **Tests**: `tests/`

### Key Patterns to Remember

1. **Always use dependency injection** - All levels get same managers
2. **Check display mode** - Optimize for DEFAULT vs QBOARD
3. **Use configuration system** - Avoid hardcoding values
4. **Implement graceful degradation** - Handle failures elegantly
5. **Cache resources** - Use ResourceManager for performance
6. **Test both modes** - Every change needs dual-mode validation

These templates provide a structured approach to common development tasks in the SS6 project, ensuring consistency with the established architecture and design philosophy.
