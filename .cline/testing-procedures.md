# Testing Procedures - SS6 Super Student Game

## Testing Philosophy

Testing in SS6 focuses on **educational effectiveness** and **deployment reliability**. Every change must be validated on both display modes and maintain the plug-and-play design philosophy.

## Test Categories

### 1. Unit Tests

**Focus**: Individual functions and methods
**Tools**: unittest, mock-based testing
**Coverage**: Critical game logic, especially manager classes

### 2. Integration Tests

**Focus**: Manager interactions and level initialization
**Tools**: Full game environment simulation
**Coverage**: Level transitions, manager state management

### 3. Display Tests

**Focus**: Both DEFAULT and QBOARD display modes
**Tools**: Display mode simulation and testing
**Coverage**: Visual scaling, performance optimization

### 4. Performance Tests

**Focus**: Frame rates and memory usage
**Tools**: Built-in profilers and custom performance tests
**Coverage**: Target hardware validation

## Test Environment Setup

### Running the Test Suite

```bash
# Run all tests
python run_tests.py

# Run specific test categories
python -m pytest tests/ -v -k "unit"
python -m pytest tests/ -v -k "integration"
python -m pytest tests/ -v -k "display"

# Run performance tests
python sound_performance_test.py
python level_sound_integration_test.py
```

### Mock Setup for Testing

```python
# Standard mock configuration for level testing
def get_mock_managers():
    return {
        'particle_manager': Mock(),
        'glass_shatter_manager': Mock(),
        'multi_touch_manager': Mock(),
        'hud_manager': Mock(),
        'checkpoint_manager': Mock(),
        'center_piece_manager': Mock(),
        'flamethrower_manager': Mock(),
        'resource_manager': Mock(),
        'config_manager': Mock(),
        'voice_generator': Mock(),
        'sound_system': Mock()
    }

# Configure common mock behaviors
def configure_mocks(mocks):
    mocks['config_manager'].get.return_value = {}
    mocks['resource_manager'].get_font.return_value = Mock()
    mocks['resource_manager'].initialize_game_resources.return_value = None
    mocks['voice_generator'].generate_voice_file.return_value = "test.wav"
```

## Display Mode Testing

### Testing Both Display Modes

```python
class DisplayModeTests(unittest.TestCase):
    def setUp(self):
        self.mocks = get_mock_managers()
        configure_mocks(self.mocks)

    def test_default_mode_optimization(self):
        """Test DEFAULT mode uses full features"""
        level = AlphabetLevel(display_mode='DEFAULT', **self.mocks)

        # Should use higher particle counts
        particle_count = level.get_particle_count()
        self.assertGreater(particle_count, 20)

        # Should use normal collision frequency
        frequency = level.get_collision_frequency()
        self.assertEqual(frequency, 1)

    def test_qboard_mode_optimization(self):
        """Test QBOARD mode uses optimized settings"""
        level = AlphabetLevel(display_mode='QBOARD', **self.mocks)

        # Should use reduced particle counts
        particle_count = level.get_particle_count()
        self.assertLess(particle_count, 15)

        # Should skip collision checks for performance
        frequency = level.get_collision_frequency()
        self.assertGreater(frequency, 1)
```

### Visual Scaling Tests

```python
def test_font_scaling():
    """Test fonts scale appropriately for each display mode"""
    for mode in ['DEFAULT', 'QBOARD']:
        level = AlphabetLevel(display_mode=mode, **get_mock_managers())

        font_size = level.get_font_size()
        if mode == 'QBOARD':
            # QBOARD should have larger fonts for touch interaction
            self.assertGreater(font_size, 48)
        else:
            # DEFAULT should use standard sizing
            self.assertEqual(font_size, 48)
```

## Manager Integration Testing

### Manager State Testing

```python
class ManagerIntegrationTests(unittest.TestCase):
    def test_manager_reset_between_levels(self):
        """Test all managers reset properly between levels"""
        # Create two different levels
        level1 = AlphabetLevel(**get_mock_managers())
        level2 = NumbersLevel(**get_mock_managers())

        # Simulate level progression
        level1.enter_level()
        level1.exit_level()
        level2.enter_level()

        # Verify managers were reset
        level1.particle_manager.reset.assert_called()
        level2.hud_manager.show_level_title.assert_called()

    def test_checkpoint_persistence(self):
        """Test checkpoint manager saves/restores state"""
        level = AlphabetLevel(**get_mock_managers())

        # Simulate game progress
        level.checkpoint_manager.save_progress.assert_not_called()

        # Trigger save
        level.on_level_complete()
        level.checkpoint_manager.save_progress.assert_called()
```

## Audio System Testing

### Voice Generation Testing

```python
class VoiceSystemTests(unittest.TestCase):
    def test_voice_generation_fallbacks(self):
        """Test voice system tries multiple generation methods"""
        mocks = get_mock_managers()
        level = AlphabetLevel(**mocks)

        # Mock ElevenLabs API failure
        mocks['voice_generator'].generate_voice_file.side_effect = Exception("API Error")

        # Should fall back to SAPI
        level.play_letter_sound('A')

        # Verify fallback was attempted
        mocks['voice_generator'].generate_sapi_voice.assert_called_with('A')

    def test_sound_loading_with_missing_files(self):
        """Test graceful handling of missing sound files"""
        mocks = get_mock_managers()
        level = AlphabetLevel(**mocks)

        # Mock file loading failure
        mocks['sound_system'].load_sound.side_effect = FileNotFoundError()

        # Should not crash, should use fallback
        try:
            level.play_sound('nonexistent.wav')
        except Exception as e:
            self.fail(f"Sound loading should not raise exception: {e}")
```

## Configuration Testing

### Configuration Loading Tests

```python
class ConfigurationTests(unittest.TestCase):
    def test_configuration_fallbacks(self):
        """Test configuration system provides safe defaults"""
        mocks = get_mock_managers()

        # Mock missing configuration file
        mocks['config_manager'].get.side_effect = FileNotFoundError()

        level = AlphabetLevel(**mocks)

        # Should still initialize with defaults
        self.assertIsNotNone(level.config)
        self.assertIsNotNone(level.display_mode)

    def test_invalid_configuration_handling(self):
        """Test handling of malformed configuration"""
        mocks = get_mock_managers()

        # Mock invalid JSON
        mocks['config_manager'].get.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)

        # Should use defaults instead of crashing
        level = AlphabetLevel(**mocks)
        self.assertEqual(level.get_particle_count(), 25)  # Default value
```

## Performance Testing

### Frame Rate Testing

```python
class PerformanceTests(unittest.TestCase):
    def test_frame_rate_requirements(self):
        """Test game maintains acceptable frame rates"""
        for mode in ['DEFAULT', 'QBOARD']:
            with self.subTest(display_mode=mode):
                # Run performance test
                fps = self.measure_average_fps(mode)

                if mode == 'DEFAULT':
                    self.assertGreaterEqual(fps, 30)  # Minimum 30 FPS
                else:  # QBOARD
                    self.assertGreaterEqual(fps, 20)  # Minimum 20 FPS for touch

    def measure_average_fps(self, display_mode):
        """Measure average FPS over test period"""
        # Implementation would run game loop and measure FPS
        return 45  # Placeholder
```

### Memory Usage Testing

```python
def test_memory_usage():
    """Test memory usage stays within acceptable limits"""
    import psutil
    import os

    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB

    # Run game for test period
    run_game_test()

    final_memory = process.memory_info().rss / 1024 / 1024  # MB
    memory_increase = final_memory - initial_memory

    # Should not leak more than 50MB during test
    assert memory_increase < 50, f"Memory leak detected: {memory_increase}MB"
```

## Manual Testing Procedures

### Pre-Release Testing Checklist

#### Installation Testing

- [ ] Clean install works with `python install.py`
- [ ] Game launches with `python SS6.origional.py`
- [ ] Auto-generated launchers work (Play.bat/Play.sh)
- [ ] No dependency errors or import failures

#### Display Mode Testing

- [ ] DEFAULT mode shows full visual effects
- [ ] QBOARD mode shows optimized performance
- [ ] Visual elements scale appropriately
- [ ] Font sizes adjust for display type
- [ ] Particle counts optimize correctly

#### Level Testing

- [ ] All levels accessible from main menu
- [ ] Level transitions work smoothly
- [ ] Manager state resets between levels
- [ ] Checkpoint system saves progress
- [ ] ESC key navigation functions properly

#### Audio Testing

- [ ] Voice generation works (ElevenLabs → SAPI → Synthetic)
- [ ] Sound effects play at correct timing
- [ ] Audio doesn't interfere with gameplay
- [ ] Missing audio files handled gracefully

#### Input Testing

- [ ] Mouse input works correctly
- [ ] Touch input normalizes properly (if available)
- [ ] Multi-touch gestures handled (if supported)
- [ ] Keyboard navigation works (ESC, etc.)

#### Performance Testing

- [ ] Frame rate acceptable on target hardware
- [ ] Memory usage stable during gameplay
- [ ] No crashes during extended play sessions
- [ ] Performance consistent across level types

### Automated Testing Integration

#### Continuous Integration Setup

```bash
# Example CI pipeline commands
python install.py
python run_tests.py
python sound_performance_test.py
python SS6.origional.py --test-mode
```

#### Test Data Management

- Use consistent test data across test runs
- Mock external dependencies (ElevenLabs API, file system)
- Reset global state between tests
- Clean up temporary files after tests

## Debugging Test Failures

### Common Test Failure Patterns

**Display Mode Issues:**

```python
# Debug display mode detection
def debug_display_mode():
    from Display_settings import detect_display_type
    print(f"Detected: {detect_display_type()}")

    # Test both modes explicitly
    for mode in ['DEFAULT', 'QBOARD']:
        print(f"Testing {mode} mode...")
        # Run tests with explicit mode
```

**Manager State Issues:**

```python
# Debug manager interactions
def debug_manager_state():
    # Enable manager state logging
    import logging
    logging.basicConfig(level=logging.DEBUG)

    # Test manager reset patterns
    level = TestLevel(**get_mock_managers())
    level.particle_manager.reset.assert_called()
```

**Configuration Issues:**

```python
# Debug configuration loading
def debug_config():
    try:
        config = get_config_manager()
        print(f"Config loaded: {config.get('test_key', 'default')}")
    except Exception as e:
        print(f"Config error: {e}")
        # Check file permissions and JSON syntax
```

## Test Documentation

### Writing Test Cases

```python
def test_feature_with_documentation():
    """
    Test feature X functionality.

    This test verifies that:
    - Feature X works in DEFAULT mode
    - Feature X works in QBOARD mode
    - Proper fallbacks are used when dependencies fail
    - Performance is acceptable on target hardware
    """
    # Test implementation
    pass
```

### Test Organization

- Group related tests in test classes
- Use descriptive test method names
- Include docstrings explaining test purpose
- Separate unit tests from integration tests
- Keep tests independent and repeatable

This testing approach ensures that all changes maintain the educational quality and deployment reliability that are core to the SS6 project philosophy.
