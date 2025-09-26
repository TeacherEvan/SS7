"""
Configuration Migration Script for SS6 Super Student Game.
Updates the codebase to use the new JSON/YAML configuration system.
"""

import logging
import os
import re
from pathlib import Path
from typing import List, Tuple


class ConfigurationMigrator:
    """
    Migrates the SS6 codebase from settings.py to JSON/YAML configuration.
    """

    def __init__(self, project_root: str):
        """
        Initialize the configuration migrator.

        Args:
            project_root: Root directory of the SS6 project
        """
        self.project_root = project_root
        self.logger = logging.getLogger(__name__)

        # Settings mappings from old to new format
        self.settings_mappings = {
            "COLORS_COLLISION_DELAY": "game.game.collision_delay",
            "LEVEL_PROGRESS_PATH": "game.game.level_progress_path",
            "WHITE": "game.colors.white",
            "BLACK": "game.colors.black",
            "FLAME_COLORS": "game.colors.flame_colors",
            "LASER_EFFECTS": "game.effects.laser_effects",
            "LETTER_SPAWN_INTERVAL": "game.game.letter_spawn_interval",
            "SEQUENCES": "game.sequences",
            "GAME_MODES": "game.game_modes",
            "GROUP_SIZE": "game.game.group_size",
        }

    def find_python_files(self) -> List[str]:
        """Find all Python files in the project."""
        python_files = []

        for root, dirs, files in os.walk(self.project_root):
            # Skip __pycache__ directories
            dirs[:] = [d for d in dirs if d != "__pycache__"]

            for file in files:
                if file.endswith(".py") and not file.startswith("."):
                    python_files.append(os.path.join(root, file))

        return python_files

    def analyze_settings_usage(self, filepath: str) -> List[Tuple[str, int, str]]:
        """
        Analyze a Python file for settings usage.

        Args:
            filepath: Path to the Python file

        Returns:
            List of (setting_name, line_number, line_content) tuples
        """
        usages = []

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                lines = f.readlines()

            for line_num, line in enumerate(lines, 1):
                for setting_name in self.settings_mappings.keys():
                    # Look for direct usage of setting constants
                    pattern = r"\b" + setting_name + r"\b"
                    if re.search(pattern, line):
                        usages.append((setting_name, line_num, line.strip()))

        except Exception as e:
            self.logger.error(f"Error analyzing {filepath}: {e}")

        return usages

    def generate_migration_imports(self) -> str:
        """Generate import statements for the new configuration system."""
        return """
# New configuration system imports
from utils.config_manager import get_config_manager

# Get configuration manager instance
config = get_config_manager()
"""

    def generate_replacement_code(self, setting_name: str) -> str:
        """
        Generate replacement code for a setting.

        Args:
            setting_name: Name of the old setting constant

        Returns:
            New configuration access code
        """
        config_path = self.settings_mappings.get(setting_name)
        if not config_path:
            return setting_name  # No replacement available

        # Handle special cases for tuple conversion
        if setting_name in ["WHITE", "BLACK"]:
            return f"tuple(config.get('{config_path}', [255, 255, 255]))"
        elif setting_name == "FLAME_COLORS":
            return f"[tuple(color) for color in config.get('{config_path}', [])]"
        else:
            return f"config.get('{config_path}')"

    def create_migration_report(self) -> str:
        """Create a detailed migration report."""
        report = []
        report.append("SS6 Configuration Migration Report")
        report.append("=" * 50)
        report.append("")

        # Find all Python files
        python_files = self.find_python_files()
        report.append(f"Found {len(python_files)} Python files to analyze")
        report.append("")

        total_usages = 0

        for filepath in python_files:
            usages = self.analyze_settings_usage(filepath)
            if usages:
                rel_path = os.path.relpath(filepath, self.project_root)
                report.append(f"File: {rel_path}")
                report.append("-" * len(f"File: {rel_path}"))

                for setting_name, line_num, line_content in usages:
                    report.append(f"  Line {line_num}: {setting_name}")
                    report.append(f"    Current: {line_content}")
                    replacement = self.generate_replacement_code(setting_name)
                    report.append(f"    Replace with: {replacement}")
                    report.append("")
                    total_usages += 1

                report.append("")

        report.append(f"Total settings usages found: {total_usages}")
        report.append("")

        # Migration steps
        report.append("Migration Steps:")
        report.append("1. Add configuration imports to each file using settings")
        report.append("2. Replace setting constants with config.get() calls")
        report.append("3. Test all functionality with new configuration system")
        report.append("4. Remove or comment out settings.py imports")
        report.append("")

        # Benefits
        report.append("Benefits of New Configuration System:")
        report.append("- Teacher-friendly JSON/YAML configuration files")
        report.append("- Runtime configuration changes without code modification")
        report.append("- Structured configuration with validation")
        report.append("- Export/import of teacher customizations")
        report.append("- Backward compatibility with legacy code")

        return "\n".join(report)

    def create_settings_compatibility_layer(self) -> str:
        """Create a compatibility layer for existing settings imports."""
        return '''"""
Settings Compatibility Layer for SS6 Super Student Game.
Provides backward compatibility while transitioning to the new configuration system.
"""

# Import the new configuration system
from utils.config_manager import get_config_manager

# Initialize configuration manager
_config = get_config_manager()

# Legacy settings constants for backward compatibility
COLORS_COLLISION_DELAY = _config.get('game.game.collision_delay', 250)
LEVEL_PROGRESS_PATH = _config.get('game.game.level_progress_path', 'level_progress.txt')
WHITE = tuple(_config.get('game.colors.white', [255, 255, 255]))
BLACK = tuple(_config.get('game.colors.black', [0, 0, 0]))
FLAME_COLORS = [tuple(color) for color in _config.get('game.colors.flame_colors', [[255, 69, 0], [255, 215, 0], [0, 191, 255]])]
LASER_EFFECTS = _config.get('game.effects.laser_effects', [])
LETTER_SPAWN_INTERVAL = _config.get('game.game.letter_spawn_interval', 60)
SEQUENCES = _config.get('game.sequences', {})
GAME_MODES = _config.get('game.game_modes', [])
GROUP_SIZE = _config.get('game.game.group_size', 5)

# Function to refresh settings (useful for runtime configuration changes)
def refresh_settings():
    """Refresh all settings from configuration files."""
    global COLORS_COLLISION_DELAY, LEVEL_PROGRESS_PATH, WHITE, BLACK
    global FLAME_COLORS, LASER_EFFECTS, LETTER_SPAWN_INTERVAL
    global SEQUENCES, GAME_MODES, GROUP_SIZE
    
    _config._load_all_configs()
    
    COLORS_COLLISION_DELAY = _config.get('game.game.collision_delay', 250)
    LEVEL_PROGRESS_PATH = _config.get('game.game.level_progress_path', 'level_progress.txt')
    WHITE = tuple(_config.get('game.colors.white', [255, 255, 255]))
    BLACK = tuple(_config.get('game.colors.black', [0, 0, 0]))
    FLAME_COLORS = [tuple(color) for color in _config.get('game.colors.flame_colors', [[255, 69, 0], [255, 215, 0], [0, 191, 255]])]
    LASER_EFFECTS = _config.get('game.effects.laser_effects', [])
    LETTER_SPAWN_INTERVAL = _config.get('game.game.letter_spawn_interval', 60)
    SEQUENCES = _config.get('game.sequences', {})
    GAME_MODES = _config.get('game.game_modes', [])
    GROUP_SIZE = _config.get('game.game.group_size', 5)

# Enhanced settings access with teacher customizations
def get_current_sequences():
    """Get sequences with teacher customizations applied."""
    sequences = {}
    base_sequences = _config.get('game.sequences', {})
    
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
'''

    def run_migration_analysis(self) -> str:
        """Run complete migration analysis and return report."""
        self.logger.info("Starting configuration migration analysis...")

        # Generate migration report
        report = self.create_migration_report()

        # Save report to file
        report_path = os.path.join(self.project_root, "config_migration_report.txt")
        try:
            with open(report_path, "w") as f:
                f.write(report)
            self.logger.info(f"Migration report saved to: {report_path}")
        except Exception as e:
            self.logger.error(f"Error saving migration report: {e}")

        return report

    def create_compatibility_layer(self):
        """Create the settings compatibility layer file."""
        compatibility_code = self.create_settings_compatibility_layer()

        # Backup original settings.py
        original_settings = os.path.join(self.project_root, "settings.py")
        backup_settings = os.path.join(self.project_root, "settings_backup.py")

        if os.path.exists(original_settings):
            try:
                import shutil

                shutil.copy2(original_settings, backup_settings)
                self.logger.info(f"Backed up original settings to: {backup_settings}")
            except Exception as e:
                self.logger.error(f"Error backing up settings: {e}")

        # Create new settings.py with compatibility layer
        try:
            with open(original_settings, "w") as f:
                f.write(compatibility_code)
            self.logger.info("Created settings compatibility layer")
        except Exception as e:
            self.logger.error(f"Error creating compatibility layer: {e}")


if __name__ == "__main__":
    # Run migration analysis
    project_root = os.path.dirname(os.path.dirname(__file__))
    migrator = ConfigurationMigrator(project_root)

    print("Running SS6 Configuration Migration Analysis...")
    print("=" * 60)

    # Generate and display report
    report = migrator.run_migration_analysis()
    print(report)

    # Ask user if they want to create compatibility layer
    response = input("\nCreate settings compatibility layer? (y/n): ").lower().strip()
    if response == "y":
        migrator.create_compatibility_layer()
        print("Compatibility layer created successfully!")
        print("The original settings.py has been backed up as settings_backup.py")
    else:
        print("Migration analysis complete. No changes made.")
