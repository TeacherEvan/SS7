# SS6 Super Student Game - AI Coding Guidelines

## Architecture Overview

SS6 is a pygame-based educational game with a **dependency injection** architecture where universal managers are passed into level classes via constructor parameters. The game features adaptive display support for both standard monitors and QBoard interactive displays.

### Core Components

- **Main Entry Point**: `SS6.origional.py` - Initializes all managers and orchestrates the game loop
- **Universal Managers**: `universal_class.py` - Contains 6 key managers (MultiTouchManager, GlassShatterManager, HUDManager, CheckpointManager, FlamethrowerManager, CenterPieceManager)
- **Level System**: `levels/` - Each game mode is a separate class with consistent constructor patterns
- **Configuration System**: `utils/config_manager.py` - New JSON/YAML-based configuration with teacher customization support
- **Settings Layer**: `settings.py` - Compatibility layer bridging old hardcoded constants to new config system
- **Resource Management**: `utils/resource_manager.py` - Handles font caching and display-aware resource scaling
- **Display Adaptation**: `Display_settings.py` - Manages DEFAULT vs QBOARD display modes with different performance profiles
- **Voice System**: `utils/voice_generator.py` - Handles text-to-speech generation using Windows SAPI with ElevenLabs fallback
- **Sound Management**: `sounds/` - Contains all audio files (voices, effects) with Windows TTS-generated pronunciation

### Critical Patterns

**Level Class Constructor Pattern**: All level classes follow the same constructor signature accepting 15+ manager dependencies:
```python
def __init__(self, width, height, screen, fonts, small_font, target_font, 
             particle_manager, glass_shatter_manager, multi_touch_manager, 
             hud_manager, checkpoint_manager, center_piece_manager, 
             flamethrower_manager, resource_manager, create_explosion_func, ...)
```

**Display Mode Adaptation**: All visual elements check `display_mode` from `PERFORMANCE_SETTINGS` for QBoard-specific optimizations:
- Font sizes scale via `FONT_SIZES[display_mode]`
- Particle counts reduce for QBoard: `collision_check_frequency = 2` vs `1`
- Visual effects disable glow on QBoard

**Resource Caching**: Text surfaces are pre-cached in ResourceManager for performance:
```python
self.center_target_cache = {}  # Cache for center target (size 900)
self.falling_object_cache = {}  # Cache for falling objects (size 240)
```

### Error Handling Patterns

**Graceful Degradation**: The game should continue functioning even when non-critical components fail:
```python
try:
    voice_generator.generate_voice_file(text, filename)
except Exception as e:
    print(f"Voice generation failed, using fallback: {e}")
    # Continue without voice or use synthetic beep
```

**Resource Loading**: Always provide fallbacks for missing resources:
```python
try:
    sound = pygame.mixer.Sound(sound_path)
except pygame.error:
    # Use silence or generate synthetic sound
```

**Display Initialization**: Handle display failures gracefully:
```python
try:
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
except pygame.error:
    # Fall back to windowed mode
    screen = pygame.display.set_mode((800, 600))
```

**File I/O**: Always handle configuration file errors:
```python
try:
    with open(config_path, 'r') as f:
        config = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    # Use default configuration
    config = get_default_config()
```

## Development Workflows

**Installation & Setup**:
```bash
python install.py  # Auto-installs pygame, creates Play.bat/Play.sh
```

**Running the Game**:
- Primary: Use generated `Play.bat` (Windows) or `Play.sh` (Linux/Mac)  
- Direct: `python SS6.origional.py`
- Entry point is always `SS6.origional.py`, NOT a main.py

**Testing & Validation**:
```bash
python run_tests.py  # Comprehensive test runner with environment setup
```

**Testing Patterns**:
- **Unit Tests**: Focus on individual manager classes and utility functions
- **Integration Tests**: Test level initialization and manager interactions
- **Performance Tests**: Validate frame rates and memory usage on different display modes
- **Mock External Dependencies**: Use mocks for file I/O, network calls, and system resources
- **Test Isolation**: Each test should be independent and reset any global state
- **Coverage**: Aim for high coverage of critical game logic, especially manager classes

**Configuration Architecture**: 
- **New System**: `config/game_config.json` - Main game settings, `config/teacher_config.yaml` - Teacher customizations
- **Legacy Bridge**: `settings.py` - Compatibility layer for existing code using old constants
- **Access Patterns**: Use `get_config_manager()` for new code, legacy constants still work in existing code
- **Migration**: Settings are automatically migrated from hardcoded values to config files

**Dependency Management**:
- **Core Dependencies**: pygame>=2.0.0, requests>=2.25.0, pyyaml>=6.0, psutil>=5.8.0
- **Optional Dependencies**: ElevenLabs API for enhanced voice generation
- **Installation**: Always use `python install.py` for setup to ensure proper dependency resolution
- **Compatibility**: Maintain Python 3.6+ compatibility for educational environments

**File Structure Best Practices**:
```
SS6/
├── SS6.origional.py         # Main entry point (never rename)
├── settings.py              # Legacy settings compatibility
├── universal_class.py       # Core manager classes
├── levels/                  # Game mode implementations
│   ├── __init__.py
│   ├── alphabet_level.py
│   ├── numbers_level.py
│   └── ...
├── utils/                   # Utility modules
│   ├── config_manager.py    # New configuration system
│   ├── resource_manager.py  # Font and resource caching
│   ├── voice_generator.py   # Text-to-speech system
│   └── ...
├── config/                  # Configuration files (some ignored)
│   ├── game_config.json     # Core settings (tracked)
│   ├── teacher_config.yaml  # Teacher customizations (tracked)
│   └── voice_config.json    # API keys (ignored)
└── sounds/                  # Audio assets (tracked)
```

**File Dependencies**: 
- `config/game_config.json` - Core game configuration (auto-created with defaults)
- `config/teacher_config.yaml` - Teacher customizations (sequences, difficulty, enabled modes)
- `config/voice_config.json` - Voice system configuration (ElevenLabs API key, TTS settings)
- `Display_settings.py` - Display modes and performance settings
- `level_progress.txt` - Persistent game state (auto-created)
- `sounds/*.wav` - Audio files generated via Windows TTS or ElevenLabs API

## Project-Specific Conventions

**Multi-Touch Event Handling**: Touch events convert normalized coordinates to screen coordinates:
```python
touch_x = event.x * self.width
touch_y = event.y * self.height
```

**Manager State Reset**: Always call `.reset()` on universal managers between levels to prevent state bleeding.

**Performance Optimization**: 
- Use `collision_frequency` from PERFORMANCE_SETTINGS to skip collision checks on alternate frames for QBoard
- Cache font surfaces in ResourceManager instead of re-rendering
- Limit particle counts based on display mode

**Level Progression**: Games use `SEQUENCES` dict from settings.py for content (alphabet, numbers, shapes, etc.) and progress in `GROUP_SIZE` chunks.

**Color Standards**: Use `FLAME_COLORS` from settings.py for consistent visual theming across all game elements.

**Voice Generation**: The game uses a multi-tier voice system:
- **Primary**: ElevenLabs API (requires API key in `config/voice_config.json`)
- **Fallback**: Windows SAPI Text-to-Speech (automatic, no setup required)
- **Last Resort**: Synthetic beeps (generated if TTS fails)
Voice files are cached in `sounds/` directory for performance.

**Security Considerations**:
- **API Keys**: Never commit API keys to version control - use `config/voice_config.json` (ignored by git)
- **File Paths**: Always validate file paths to prevent directory traversal attacks
- **User Input**: Sanitize any configuration input to prevent injection attacks
- **Network Requests**: Use HTTPS only for ElevenLabs API calls with timeout and retry limits
- **File Permissions**: Ensure game only writes to its own directory structure
- **Configuration**: Validate configuration values and use safe defaults

**Configuration Access Patterns**: 
- **New Code**: Use `from utils.config_manager import get_config_manager` then `config = get_config_manager()` and `config.get('path.to.setting', default_value)`
- **Legacy Code**: Import constants from `settings.py` (e.g., `from settings import SEQUENCES, COLORS`)
- **Teacher Customizations**: Use `config.get_custom_sequence(type)` and `config.is_game_mode_enabled(mode)`
- **Runtime Updates**: Call `config.reload()` or `settings.refresh_settings()` to pick up config file changes

**Alphabet Level Enhancement Requirements**: 
- **Visual Emoji Integration**: Each letter (A-Z) must drop down with 2 PNG emoji representations
- **Letter-Emoji Association**: Use standard associations (A=Apple, B=Ball, C=Cat, etc.)
- **Asset Structure**: Store emoji PNGs in `assets/emojis/` directory organized by letter
- **Pronunciation Integration**: Play letter pronunciation immediately when target is hit
- **Visual Feedback**: Emojis should animate alongside letters with matching timing
- **Resource Loading**: Pre-cache emoji surfaces in ResourceManager for performance
- **Display Scaling**: Emojis must scale appropriately for DEFAULT vs QBOARD display modes

## Key Integration Points

- **Pygame Event Loop**: Multi-touch (FINGERDOWN/UP/MOTION) + mouse + keyboard in `SS6.origional.py`
- **State Persistence**: Level progress saved to `level_progress.txt` via CheckpointManager
- **Display Auto-Detection**: `detect_display_type()` in Display_settings.py determines initial mode
- **Font Scaling**: ResourceManager.initialize_game_resources() must be called after display mode changes

When adding new levels, follow the existing constructor pattern and ensure all universal managers are properly injected and reset between levels.

## Debugging and Troubleshooting

**Common Issues**:
- **Import Errors**: Ensure all files are in correct locations and Python path is set
- **Display Issues**: Check `Display_settings.py` for display mode configuration
- **Audio Problems**: Verify pygame mixer initialization and file paths
- **Performance Issues**: Check particle counts and collision detection frequency
- **Configuration Errors**: Validate JSON/YAML syntax and file permissions

**Debugging Tools**:
- **Memory Profiler**: Use `utils/memory_profiler.py` to track memory usage
- **Debug Display**: Enable debug information in `utils/debug_display.py`
- **Event Tracking**: Monitor game events with `utils/event_tracker.py`
- **Performance Metrics**: Use frame rate monitoring for optimization

**Logging Patterns**:
```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Use structured logging for debugging
logger.info(f"Level initialized: {level_name}, particles: {particle_count}")
```

**Testing Specific Scenarios**:
- Test with `DISPLAY_MODE = 'QBOARD'` for performance optimization validation
- Test level transitions and manager state resets
- Test configuration file loading and fallback scenarios
- Test multi-touch functionality if available

## Alphabet Level Emoji Implementation Guide

**Asset Organization**:
```
assets/
├── emojis/
│   ├── A_apple_1.png
│   ├── A_apple_2.png
│   ├── B_ball_1.png
│   ├── B_ball_2.png
│   └── ... (continuing for all 26 letters)
```

**Standard Letter-Emoji Associations**:
- A: Apple, Ant
- B: Ball, Banana
- C: Cat, Car
- D: Dog, Duck
- E: Elephant, Egg
- F: Fish, Flower
- G: Giraffe, Grapes
- H: House, Hat
- I: Ice Cream, Iguana
- J: Jar, Juice
- K: Kite, Key
- L: Lion, Leaf
- M: Mouse, Moon
- N: Nest, Nose
- O: Orange, Owl
- P: Penguin, Pizza
- Q: Queen, Question Mark
- R: Rainbow, Rabbit
- S: Sun, Snake
- T: Tree, Tiger
- U: Umbrella, Unicorn
- V: Violin, Volcano
- W: Whale, Watermelon
- X: X-ray, Xylophone
- Y: Yarn, Yacht
- Z: Zebra, Zipper

**Implementation Requirements**:
- Emojis drop simultaneously with letters
- Both emojis appear for each letter target
- Voice pronunciation triggers on successful letter hit
- Smooth animation timing synchronized with particle effects
- Proper scaling for different display modes
- Resource pre-loading for performance optimization

## Contributing Guidelines

**Code Quality Standards**:
- Follow existing code patterns and naming conventions
- Add type hints for new functions where helpful
- Include docstrings for complex functions and classes
- Test new features with the existing test framework
- Ensure backwards compatibility with existing save files

**Pull Request Guidelines**:
- Keep changes focused and atomic
- Test changes on both DEFAULT and QBOARD display modes
- Verify that existing levels continue to work
- Run `python run_tests.py` before submitting
- Document any new configuration options

**Development Environment**:
- Use Python 3.6+ for compatibility
- Install dependencies via `python install.py`
- Test on multiple display resolutions if possible
- Respect the plug-and-play design philosophy

**Code Review Checklist**:
- No hardcoded values (use configuration system)
- Proper error handling with graceful degradation
- Memory efficient (use object pooling for particles)
- Performance conscious (cache resources, limit particle counts)
- Educational focus maintained (simple, distraction-free interface)

## CRITICAL PROJECT CONSTRAINTS

**❌ DO NOT ADD:**
- **Achievements system** - Not wanted in this application
- **Progress tracking beyond basic level progression** - Keep it simple
- **User profiles or accounts** - This is a plug-and-play educational tool
- **Complex data persistence** - Only `level_progress.txt` for basic state
- **Analytics or telemetry** - No data collection features
- **Social features** - No sharing, leaderboards, or online connectivity
- **Settings menus or configuration GUIs** - No complex settings interfaces
- **Display mode selectors** - Game auto-detects appropriate display mode

**✅ MAINTAIN PLUG-AND-PLAY DESIGN:**
- **Zero setup required** - Run `python SS6.origional.py` and play immediately
- **Self-contained** - All dependencies included or auto-installed via `install.py`
- **No external services** - No internet connectivity required
- **Simple file structure** - Keep the current clean organization
- **Minimal configuration** - Automatic configuration only, no user settings
- **Simplified UI** - Clean, distraction-free interface focused on gameplay

**DESIGN PHILOSOPHY:** This is an educational tool that should "just work" when deployed to classrooms, libraries, or homes without any setup complexity, user accounts, settings menus, or data tracking concerns. The interface should be as simple as possible - just the game and learning content.

**CURRENT UI FLOW:**
1. **Welcome Screen** - Simple particle animation with "click to continue"
2. **Level Menu** - Direct selection of game modes (Alphabet, Numbers, Shapes, etc.)
3. **Game Levels** - Pure gameplay with minimal UI distractions
4. **Navigation** - ESC key returns to previous screen (levels → menu → exit)