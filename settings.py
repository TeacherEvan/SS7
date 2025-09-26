"""
Settings Compatibility Layer for SS6 Super Student Game.
Provides backward compatibility while transitioning to the new configuration system.
"""

# Import the new configuration system
from utils.config_manager import get_config_manager

# Initialize configuration manager
_config = get_config_manager()

# Legacy settings constants for backward compatibility
COLORS_COLLISION_DELAY = _config.get("game.game.collision_delay", 250)
LEVEL_PROGRESS_PATH = _config.get("game.game.level_progress_path", "level_progress.txt")
WHITE = tuple(_config.get("game.colors.white", [255, 255, 255]))
BLACK = tuple(_config.get("game.colors.black", [0, 0, 0]))
FLAME_COLORS = [
    tuple(color)
    for color in _config.get(
        "game.colors.flame_colors", [[255, 69, 0], [255, 215, 0], [0, 191, 255]]
    )
]
LASER_EFFECTS = _config.get("game.effects.laser_effects", [])
LETTER_SPAWN_INTERVAL = _config.get("game.game.letter_spawn_interval", 60)
SEQUENCES = _config.get("game.sequences", {})
GAME_MODES = _config.get("game.game_modes", [])
GROUP_SIZE = _config.get("game.game.group_size", 5)


# Function to refresh settings (useful for runtime configuration changes)
def refresh_settings():
    """Refresh all settings from configuration files."""
    global COLORS_COLLISION_DELAY, LEVEL_PROGRESS_PATH, WHITE, BLACK
    global FLAME_COLORS, LASER_EFFECTS, LETTER_SPAWN_INTERVAL
    global SEQUENCES, GAME_MODES, GROUP_SIZE

    _config._load_all_configs()

    COLORS_COLLISION_DELAY = _config.get("game.game.collision_delay", 250)
    LEVEL_PROGRESS_PATH = _config.get("game.game.level_progress_path", "level_progress.txt")
    WHITE = tuple(_config.get("game.colors.white", [255, 255, 255]))
    BLACK = tuple(_config.get("game.colors.black", [0, 0, 0]))
    FLAME_COLORS = [
        tuple(color)
        for color in _config.get(
            "game.colors.flame_colors", [[255, 69, 0], [255, 215, 0], [0, 191, 255]]
        )
    ]
    LASER_EFFECTS = _config.get("game.effects.laser_effects", [])
    LETTER_SPAWN_INTERVAL = _config.get("game.game.letter_spawn_interval", 60)
    SEQUENCES = _config.get("game.sequences", {})
    GAME_MODES = _config.get("game.game_modes", [])
    GROUP_SIZE = _config.get("game.game.group_size", 5)


# Enhanced settings access with teacher customizations
def get_current_sequences():
    """Get sequences with teacher customizations applied."""
    sequences = {}
    base_sequences = _config.get("game.sequences", {})

    for seq_type in base_sequences.keys():
        sequences[seq_type] = _config.get_custom_sequence(seq_type)

    return sequences


def get_enabled_game_modes():
    """Get currently enabled game modes based on teacher settings."""
    return [mode for mode in GAME_MODES if _config.is_game_mode_enabled(mode)]


def get_difficulty_settings():
    """Get current difficulty settings."""
    return _config.get_difficulty_settings()


# Configuration manager access for advanced usage
def get_configuration_manager():
    """Get the configuration manager instance for advanced usage."""
    return _config
