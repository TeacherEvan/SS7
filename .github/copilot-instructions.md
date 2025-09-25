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

**Configuration Architecture**: 
- **New System**: `config/game_config.json` - Main game settings, `config/teacher_config.yaml` - Teacher customizations
- **Legacy Bridge**: `settings.py` - Compatibility layer for existing code using old constants
- **Access Patterns**: Use `get_config_manager()` for new code, legacy constants still work in existing code
- **Migration**: Settings are automatically migrated from hardcoded values to config files

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