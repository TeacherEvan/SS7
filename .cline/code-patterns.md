# Code Patterns - SS6 Super Student Game

## Essential Patterns for SS6 Development

### 1. Level Class Constructor Pattern

**All level classes must follow this exact signature:**

```python
def __init__(self, width, height, screen, fonts, small_font, target_font,
             particle_manager, glass_shatter_manager, multi_touch_manager,
             hud_manager, checkpoint_manager, center_piece_manager,
             flamethrower_manager, resource_manager, create_explosion_func,
             display_mode, voice_generator, sound_system, config_manager):
    # Store essential references
    self.display_mode = display_mode
    self.resource_manager = resource_manager
    self.voice_generator = voice_generator
    self.config_manager = config_manager
    self.hud_manager = hud_manager

    # Get level-specific configuration
    self.level_config = self.config_manager.get('levels.alphabet_level', {})
```

### 2. Display Mode Optimization Pattern

**Always optimize for both display modes:**

```python
class VisualElement:
    def __init__(self, display_mode, config_manager):
        self.display_mode = display_mode
        self.config = config_manager

        # Get display-specific settings
        self.particle_count = self.get_optimized_particle_count()
        self.font_size = self.get_optimized_font_size()
        self.update_frequency = self.get_optimized_frequency()

    def get_optimized_particle_count(self):
        base_count = self.config.get('particles.base_count', 25)
        if self.display_mode == 'QBOARD':
            return max(5, base_count // 2)  # Minimum 5 particles
        return base_count

    def get_optimized_font_size(self):
        base_size = self.config.get('fonts.default_size', 48)
        if self.display_mode == 'QBOARD':
            return base_size + 4  # Larger for interactive displays
        return base_size

    def get_optimized_frequency(self):
        base_freq = self.config.get('performance.collision_frequency', 1)
        if self.display_mode == 'QBOARD':
            return base_freq * 2  # Skip frames for performance
        return base_freq
```

### 3. Resource Caching Pattern

**Use ResourceManager for all surface caching:**

```python
class CachedElement:
    def __init__(self, resource_manager, display_mode):
        self.resource_manager = resource_manager
        self.display_mode = display_mode
        self.cached_surfaces = {}

    def get_cached_surface(self, text, font_size, color):
        cache_key = f"{text}_{font_size}_{color}_{self.display_mode}"

        if cache_key not in self.cached_surfaces:
            # Create new surface and cache it
            font = self.resource_manager.get_font(font_size, self.display_mode)
            surface = font.render(text, True, color)
            self.cached_surfaces[cache_key] = surface

        return self.cached_surfaces[cache_key]
```

### 4. Voice Generation Pattern

**Multi-tier voice system with fallbacks:**

```python
class VoiceEnabledFeature:
    def __init__(self, voice_generator):
        self.voice_generator = voice_generator

    def play_voice(self, text, cache_file=None):
        """Play voice with multiple fallback methods"""
        if cache_file:
            # Try cached file first
            try:
                self.voice_generator.play_cached_voice(cache_file)
                return
            except Exception as e:
                print(f"Cached voice failed: {e}")

        # Try to generate and play voice
        try:
            # Method 1: ElevenLabs API (if configured)
            temp_file = self.voice_generator.generate_voice_file(text)
            self.voice_generator.play_voice_file(temp_file)
        except Exception as e:
            try:
                # Method 2: Windows SAPI TTS
                self.voice_generator.generate_sapi_voice(text)
                self.voice_generator.play_voice_file(temp_file)
            except Exception as e:
                # Method 3: Synthetic fallback
                print(f"All voice methods failed: {e}")
                self.play_synthetic_fallback(text)
```

### 5. Configuration Access Pattern

**Safe configuration access with fallbacks:**

```python
class ConfigurableFeature:
    def __init__(self, config_manager):
        self.config = config_manager

    def get_config_value(self, path, default=None, expected_type=None):
        """Safely get configuration value with type checking"""
        try:
            value = self.config.get(path, default)

            # Type validation if specified
            if expected_type and not isinstance(value, expected_type):
                print(f"Warning: Expected {expected_type} for {path}, got {type(value)}")
                return default

            return value
        except Exception as e:
            print(f"Config access error for {path}: {e}")
            return default

    def get_display_specific_value(self, base_path, default_value):
        """Get value optimized for current display mode"""
        # Try display-specific value first
        specific_path = f"{base_path}.{self.display_mode.lower()}"
        value = self.get_config_value(specific_path, None)

        if value is not None:
            return value

        # Fall back to base value
        return self.get_config_value(base_path, default_value)
```

### 6. Event Handling Pattern

**Multi-touch and mouse event handling:**

```python
class EventHandler:
    def __init__(self, multi_touch_manager):
        self.touch_manager = multi_touch_manager
        self.last_touch_position = None

    def handle_event(self, event):
        if event.type == pygame.FINGERDOWN:
            # Normalize touch coordinates
            x = event.x * self.screen_width
            y = event.y * self.screen_height
            self.handle_touch_down(x, y, event.finger_id)

        elif event.type == pygame.FINGERUP:
            x = event.x * self.screen_width
            y = event.y * self.screen_height
            self.handle_touch_up(x, y, event.finger_id)

        elif event.type == pygame.FINGERMOTION:
            x = event.x * self.screen_width
            y = event.y * self.screen_height
            self.handle_touch_motion(x, y, event.finger_id)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.handle_mouse_down(event.pos[0], event.pos[1])

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.handle_escape()

    def handle_touch_down(self, x, y, finger_id):
        """Handle touch press - normalize coordinates"""
        self.touch_manager.register_touch(finger_id, x, y)
        self.on_touch_press(x, y)

    def handle_mouse_down(self, x, y):
        """Handle mouse press"""
        self.on_touch_press(x, y)  # Same logic as touch
```

### 7. Manager State Management Pattern

**Proper manager lifecycle management:**

```python
class LevelWithManagers:
    def __init__(self, all_managers):
        # Store manager references
        self.particle_manager = all_managers['particle_manager']
        self.glass_shatter_manager = all_managers['glass_shatter_manager']
        self.hud_manager = all_managers['hud_manager']
        # ... etc

    def enter_level(self):
        """Called when level becomes active"""
        # Reset managers to clean state
        self.particle_manager.reset()
        self.glass_shatter_manager.reset()
        self.hud_manager.reset()

        # Initialize level-specific state
        self.hud_manager.show_level_title(self.level_name)

    def exit_level(self):
        """Called when leaving level"""
        # Save any persistent state
        self.hud_manager.hide_level_title()

        # Clean up level-specific resources
        self.particle_manager.clear_all_particles()
```

### 8. Error Handling Pattern

**Graceful degradation for all operations:**

```python
class RobustFeature:
    def __init__(self):
        self.fallback_values = {}

    def safe_operation(self, primary_func, fallback_func=None, emergency_func=None):
        """Execute operation with multiple fallback levels"""
        try:
            # Primary method
            return primary_func()
        except Exception as e:
            print(f"Primary method failed: {e}")

            if fallback_func:
                try:
                    # First fallback
                    return fallback_func()
                except Exception as e:
                    print(f"Fallback method failed: {e}")

            if emergency_func:
                try:
                    # Emergency fallback
                    return emergency_func()
                except Exception as e:
                    print(f"Emergency fallback failed: {e}")

            # Return safe default
            return self.get_safe_default()

    def load_resource(self, resource_path):
        """Load resource with multiple fallback strategies"""
        return self.safe_operation(
            primary_func=lambda: self.load_primary_resource(resource_path),
            fallback_func=lambda: self.load_fallback_resource(resource_path),
            emergency_func=lambda: self.create_default_resource()
        )
```

### 9. Performance Monitoring Pattern

**Built-in performance tracking:**

```python
class PerformanceAware:
    def __init__(self):
        self.frame_count = 0
        self.last_fps_update = 0
        self.fps_samples = []

    def update(self):
        """Update with performance monitoring"""
        current_time = pygame.time.get_ticks()

        # Update FPS calculation
        if current_time - self.last_fps_update > 1000:  # Every second
            fps = len(self.fps_samples)
            print(f"FPS: {fps}")

            # Reset for next calculation
            self.fps_samples = []
            self.last_fps_update = current_time

        self.fps_samples.append(current_time)
        self.frame_count += 1

        # Actual update logic
        self.do_update()

    def do_update(self):
        """Override with actual update logic"""
        pass
```

### 10. Testing Pattern

**Mock-based testing for manager dependencies:**

```python
class TestableLevel(unittest.TestCase):
    def setUp(self):
        """Set up test with mock managers"""
        self.mock_managers = {
            'particle_manager': Mock(),
            'hud_manager': Mock(),
            'resource_manager': Mock(),
            'config_manager': Mock()
        }

        # Configure mock behaviors
        self.mock_managers['config_manager'].get.return_value = {}
        self.mock_managers['resource_manager'].get_font.return_value = Mock()

        # Create level instance with mocks
        self.level = AlphabetLevel(
            width=800, height=600, screen=Mock(),
            config_manager=self.mock_managers['config_manager'],
            **self.mock_managers
        )

    def test_level_initialization(self):
        """Test that level initializes correctly"""
        self.assertIsNotNone(self.level.display_mode)
        self.assertIsNotNone(self.level.resource_manager)

    def test_display_mode_optimization(self):
        """Test QBOARD vs DEFAULT optimization"""
        # Test DEFAULT mode
        self.level.display_mode = 'DEFAULT'
        default_count = self.level.get_particle_count()
        self.assertGreater(default_count, 10)

        # Test QBOARD mode
        self.level.display_mode = 'QBOARD'
        qboard_count = self.level.get_particle_count()
        self.assertLess(qboard_count, default_count)
```

## Pattern Usage Guidelines

### When to Use Each Pattern

1. **Constructor Pattern**: Every level class without exception
2. **Display Mode Pattern**: Every visual or performance-sensitive feature
3. **Resource Caching**: Any frequently rendered text or graphics
4. **Voice Generation**: Any text-to-speech functionality
5. **Configuration Access**: Any configurable behavior
6. **Event Handling**: All user input processing
7. **Manager State**: Level lifecycle management
8. **Error Handling**: All file I/O, network, and resource operations
9. **Performance Monitoring**: Development and optimization
10. **Testing Pattern**: All new functionality

### Pattern Combination Example

```python
class AlphabetLevel(VisualElement, VoiceEnabledFeature, EventHandler):
    """Example combining multiple patterns"""

    def __init__(self, width, height, screen, fonts, small_font, target_font,
                 particle_manager, glass_shatter_manager, multi_touch_manager,
                 hud_manager, checkpoint_manager, center_piece_manager,
                 flamethrower_manager, resource_manager, create_explosion_func,
                 display_mode, voice_generator, sound_system, config_manager):

        # Initialize parent patterns
        VisualElement.__init__(self, display_mode, config_manager)
        VoiceEnabledFeature.__init__(self, voice_generator)
        EventHandler.__init__(self, multi_touch_manager)

        # Store additional references
        self.resource_manager = resource_manager
        self.hud_manager = hud_manager
        self.particle_manager = particle_manager

        # Get configuration
        self.config = ConfigurableFeature(config_manager)
        self.letter_sounds = self.load_letter_sounds()

    def load_letter_sounds(self):
        """Load sounds with proper error handling"""
        return self.config.safe_operation(
            primary_func=self.load_primary_sounds,
            fallback_func=self.load_fallback_sounds,
            emergency_func=self.create_default_sounds
        )
```

These patterns ensure consistent, maintainable code that works across both display modes and maintains the project's educational focus and plug-and-play design philosophy.
