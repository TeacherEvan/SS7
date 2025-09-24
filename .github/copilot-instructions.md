# SS6 Super Student Game - AI Coding Guidelines

## Architecture Overview

SS6 is a pygame-based educational game with a **dependency injection** architecture where universal managers are passed into level classes via constructor parameters. The game features adaptive display support for both standard monitors and QBoard interactive displays.

### Core Components

- **Main Entry Point**: `SS6.origional.py` - Initializes all managers and orchestrates the game loop
- **Universal Managers**: `universal_class.py` - Contains 6 key managers (MultiTouchManager, GlassShatterManager, HUDManager, CheckpointManager, FlamethrowerManager, CenterPieceManager)
- **Level System**: `levels/` - Each game mode is a separate class with consistent constructor patterns
- **Resource Management**: `utils/resource_manager.py` - Handles font caching and display-aware resource scaling
- **Display Adaptation**: `Display_settings.py` - Manages DEFAULT vs QBOARD display modes with different performance profiles

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

**File Dependencies**: 
- `settings.py` - Game constants (SEQUENCES, COLORS, GAME_MODES)
- `Display_settings.py` - Display modes and performance settings
- `level_progress.txt` - Persistent game state (auto-created)

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

## Key Integration Points

- **Pygame Event Loop**: Multi-touch (FINGERDOWN/UP/MOTION) + mouse + keyboard in `SS6.origional.py`
- **State Persistence**: Level progress saved to `level_progress.txt` via CheckpointManager
- **Display Auto-Detection**: `detect_display_type()` in Display_settings.py determines initial mode
- **Font Scaling**: ResourceManager.initialize_game_resources() must be called after display mode changes

When adding new levels, follow the existing constructor pattern and ensure all universal managers are properly injected and reset between levels.

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