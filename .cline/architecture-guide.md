# Architecture Guide - SS6 Super Student Game

## Universal Manager System

The project uses a **dependency injection architecture** where all level classes receive the same set of universal managers through their constructors. This ensures consistent behavior and shared state across all game modes.

### Core Managers (universal_class.py)

1. **MultiTouchManager**: Handles touch input normalization and gesture recognition
2. **GlassShatterManager**: Manages glass shattering visual effects
3. **HUDManager**: Controls heads-up display elements and game state UI
4. **CheckpointManager**: Handles level progression and state persistence
5. **FlamethrowerManager**: Manages flame visual effects and interactions
6. **CenterPieceManager**: Controls central game elements and animations

### Manager Injection Pattern

All level classes follow this constructor signature:

```python
def __init__(self, width, height, screen, fonts, small_font, target_font,
             particle_manager, glass_shatter_manager, multi_touch_manager,
             hud_manager, checkpoint_manager, center_piece_manager,
             flamethrower_manager, resource_manager, create_explosion_func,
             display_mode, voice_generator, sound_system, config_manager):
```

## Display Adaptation System

### Display Modes

- **DEFAULT**: Standard monitors (full visual effects, higher particle counts)
- **QBOARD**: Interactive displays (optimized performance, reduced effects)

### Implementation Pattern

```python
# Check display mode for all visual elements
if display_mode == 'QBOARD':
    particle_count = 10  # Reduced for performance
    collision_frequency = 2  # Skip every other frame
else:
    particle_count = 25  # Full effects
    collision_frequency = 1  # Check every frame
```

## Configuration System

### Architecture

- **New System**: `utils/config_manager.py` - JSON/YAML-based configuration
- **Legacy Bridge**: `settings.py` - Compatibility layer for existing constants
- **Teacher Customization**: `config/teacher_config.yaml` - Educational content customization

### Access Patterns

```python
# New configuration system
from utils.config_manager import get_config_manager
config = get_config_manager()
font_size = config.get('display.font_sizes.default', 48)

# Legacy constants (still supported)
from settings import FONT_SIZES, SEQUENCES
font_size = FONT_SIZES['DEFAULT']
```

## Resource Management

### ResourceManager (utils/resource_manager.py)

Pre-caches frequently used surfaces and handles display-aware scaling:

```python
# Initialize resources for current display mode
resource_manager.initialize_game_resources(display_mode)

# Get cached surfaces
center_target = resource_manager.get_center_target(font_size)
falling_object = resource_manager.get_falling_object(letter, font_size)
```

### Caching Strategy

- **Center Target Cache**: Pre-rendered text surfaces (size 900)
- **Falling Object Cache**: Letter/number/shape surfaces (size 240)
- **Font Cache**: Display-mode-specific font loading
- **Emoji Cache**: Visual asset preloading for alphabet levels

## Voice Generation System

### Multi-Tier Architecture

1. **Primary**: ElevenLabs API (requires `config/voice_config.json`)
2. **Fallback**: Windows SAPI Text-to-Speech (automatic)
3. **Last Resort**: Synthetic beeps (generated)

### Implementation Pattern

```python
try:
    # Try ElevenLabs API first
    voice_generator.generate_voice_file(text, filename)
except Exception as e:
    try:
        # Fall back to Windows TTS
        voice_generator.generate_sapi_voice(text, filename)
    except Exception as e:
        # Generate synthetic fallback
        voice_generator.generate_synthetic_beep(frequency, filename)
```

## Sound System Architecture

### File Organization

```
sounds/
├── voice_cache/           # Generated voice files
├── emoji_*.wav           # Emoji sound effects
├── [a-z].wav             # Letter pronunciations
├── [0-9].wav             # Number pronunciations
├── *.wav                 # Shape/color pronunciations
└── welcome_*.wav         # Welcome messages
```

### Sound Loading Pattern

```python
try:
    sound = pygame.mixer.Sound(sound_path)
except pygame.error:
    # Create silence or synthetic sound
    sound = create_synthetic_sound(frequency, duration)
```

## Event Handling System

### Multi-Input Support

- **Mouse Events**: Standard pygame mouse input
- **Touch Events**: FINGERDOWN/UP/MOTION with coordinate normalization
- **Keyboard Events**: ESC for navigation, other keys as needed

### Touch Normalization

```python
# Convert touch coordinates to screen coordinates
touch_x = event.x * self.width   # event.x is normalized (0.0-1.0)
touch_y = event.y * self.height  # event.y is normalized (0.0-1.0)
```

## State Management

### CheckpointManager

- **File**: `level_progress.txt` (auto-created)
- **Format**: Simple text file with level progression data
- **Reset Pattern**: Call `checkpoint_manager.reset()` between levels

### Manager State Reset

```python
# Reset all managers between levels
multi_touch_manager.reset()
glass_shatter_manager.reset()
hud_manager.reset()
checkpoint_manager.reset()
flamethrower_manager.reset()
center_piece_manager.reset()
```

## Performance Optimization Patterns

### Particle System Optimization

```python
# Reduce particles for QBOARD mode
max_particles = 50 if display_mode == 'DEFAULT' else 20

# Skip collision checks on alternate frames
if frame_count % collision_frequency == 0:
    check_collisions()
```

### Memory Management

- **Object Pooling**: Reuse particle objects instead of creating/destroying
- **Surface Caching**: Pre-render and cache frequently used graphics
- **Sound Caching**: Keep sounds in memory to avoid repeated loading

### Display-Specific Optimizations

```python
# QBOARD optimizations
if display_mode == 'QBOARD':
    # Disable glow effects
    enable_glow = False
    # Reduce shadow complexity
    shadow_quality = 'simple'
    # Limit concurrent animations
    max_animations = 3
```

## Error Handling Architecture

### Graceful Degradation Pattern

```python
try:
    # Primary method
    result = primary_operation()
except Exception as e:
    try:
        # First fallback
        result = fallback_operation()
    except Exception as e:
        # Last resort fallback
        result = emergency_fallback()
```

### Resource Loading Fallbacks

```python
try:
    with open(config_path, 'r') as f:
        config = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    config = get_default_config()
```

## Integration Points

### Pygame Event Loop Integration

All input handling flows through the main event loop in `SS6.origional.py`:

- Touch events → MultiTouchManager
- Display events → Display_settings.py
- Game state → Universal managers
- Audio → Voice/sound systems

### Level Transition Pattern

1. Save current level state to CheckpointManager
2. Reset all universal managers
3. Initialize new level with same manager instances
4. Restore minimal state from CheckpointManager

This architecture ensures consistent behavior across all game modes while maintaining the plug-and-play design philosophy.
