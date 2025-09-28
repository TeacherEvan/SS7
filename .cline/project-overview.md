# SS6 Super Student Game - Cline Agent Instructions

## Project Overview

SS6 is a pygame-based educational game designed for classroom environments with a **plug-and-play philosophy**. The game features adaptive display support for both standard monitors and QBoard interactive displays, with a focus on simplicity and educational effectiveness.

### Core Educational Goals

- **Letter Recognition**: Alphabet learning with visual emoji associations
- **Number Recognition**: Numerical understanding through interactive gameplay
- **Shape Recognition**: Geometric shape identification
- **Color Recognition**: Color learning and identification
- **Case Learning**: Uppercase and lowercase letter mastery

### Design Philosophy

- **Zero Configuration**: Game should work immediately after installation
- **No User Accounts**: Simple, anonymous educational tool
- **No External Dependencies**: Self-contained with automatic fallback systems
- **Classroom Ready**: Optimized for interactive displays and multi-touch
- **Distraction-Free**: Clean interface focused purely on learning

## Technical Architecture

### Entry Point

- **Primary**: `SS6.origional.py` - Main game orchestrator (never rename)
- **Launchers**: `Play.bat` (Windows) / `Play.sh` (Unix) - Auto-generated wrappers

### Core Systems

1. **Universal Manager System**: Six key managers injected into all levels
2. **Display Adaptation**: Automatic detection and optimization for display type
3. **Configuration System**: JSON/YAML-based with legacy compatibility layer
4. **Resource Management**: Caching system for fonts and display resources
5. **Voice System**: Multi-tier TTS with ElevenLabs API fallback to Windows SAPI
6. **Sound System**: Pre-generated audio files for letters, numbers, shapes, colors

### Display Modes

- **DEFAULT**: Standard monitor optimization (full features)
- **QBOARD**: Interactive display optimization (reduced particles, optimized performance)

## Critical Project Constraints

### DO NOT ADD

- ❌ Achievement systems or progress tracking
- ❌ User profiles or accounts
- ❌ Analytics or telemetry
- ❌ Social features or online connectivity
- ❌ Complex settings menus or configuration GUIs
- ❌ Display mode selectors (auto-detected)

### MAINTAIN

- ✅ Plug-and-play design (zero setup required)
- ✅ Self-contained installation
- ✅ Simple, distraction-free interface
- ✅ Educational focus without gamification
- ✅ Automatic configuration and display detection

## Quick Start Commands

```bash
# Install dependencies
python install.py

# Run the game
python SS6.origional.py

# Run tests
python run_tests.py

# Generate all sounds (if needed)
python generate_all_sounds.py
```

## File Structure Highlights

```
SS6/
├── SS6.origional.py          # Main entry point
├── universal_class.py        # Core manager classes
├── settings.py              # Legacy compatibility layer
├── levels/                  # Game mode implementations
├── utils/                   # Utility systems
│   ├── config_manager.py    # Configuration system
│   ├── resource_manager.py  # Resource caching
│   ├── voice_generator.py   # Text-to-speech system
│   └── ...
├── config/                  # Configuration files
├── sounds/                  # Audio assets
└── assets/emojis/           # Visual learning assets
```

## Agent Workflow Guidelines

When working with this project:

1. **Always start from `SS6.origional.py`** - This is the single entry point
2. **Respect the manager pattern** - All levels receive the same 15+ manager dependencies
3. **Test both display modes** - Changes should work on DEFAULT and QBOARD
4. **Use configuration system** - Avoid hardcoding values
5. **Maintain plug-and-play design** - No setup complexity for end users
6. **Follow educational focus** - Keep interface simple and learning-centered

## Common Task Patterns

- **Adding new levels**: Follow constructor pattern with all manager dependencies
- **Modifying visuals**: Check display mode and scale appropriately
- **Adding sounds**: Use voice generation system with fallbacks
- **Configuration changes**: Update both JSON and legacy compatibility layer
- **Resource management**: Cache new assets in ResourceManager
- **Testing**: Validate on both display modes and test level transitions

This project prioritizes educational effectiveness and deployment simplicity over feature complexity.
