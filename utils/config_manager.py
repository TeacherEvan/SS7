"""
Configuration Manager for SS6 Super Student Game.
Handles loading and saving of game settings from JSON/YAML files.
"""

import json
import os
import yaml
import logging
from typing import Dict, Any, Optional, Union
from pathlib import Path

class ConfigurationManager:
    """
    Manages game configuration with JSON/YAML support and fallback to defaults.
    """
    
    def __init__(self, config_dir: str = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_dir: Directory containing configuration files
        """
        self.config_dir = config_dir or os.path.join(os.path.dirname(os.path.dirname(__file__)), "config")
        self.game_config_path = os.path.join(self.config_dir, "game_config.json")
        self.teacher_config_path = os.path.join(self.config_dir, "teacher_config.yaml")
        
        # Ensure config directory exists
        os.makedirs(self.config_dir, exist_ok=True)
        
        # Configuration cache
        self._config_cache = {}
        self._loaded = False
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Load configurations
        self._load_all_configs()
    
    def _load_all_configs(self):
        """Load all configuration files."""
        try:
            # Load main game configuration
            self._config_cache['game'] = self._load_json_config(self.game_config_path, self._get_default_game_config())
            
            # Load teacher customization configuration
            self._config_cache['teacher'] = self._load_yaml_config(self.teacher_config_path, self._get_default_teacher_config())
            
            self._loaded = True
            self.logger.info("All configurations loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Error loading configurations: {e}")
            self._config_cache = {
                'game': self._get_default_game_config(),
                'teacher': self._get_default_teacher_config()
            }
    
    def _load_json_config(self, filepath: str, default_config: Dict) -> Dict:
        """Load JSON configuration with fallback to defaults."""
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults for missing keys
                    return self._merge_configs(default_config, config)
            except Exception as e:
                self.logger.error(f"Error loading JSON config {filepath}: {e}")
        
        # Create default config file
        self._save_json_config(filepath, default_config)
        return default_config
    
    def _load_yaml_config(self, filepath: str, default_config: Dict) -> Dict:
        """Load YAML configuration with fallback to defaults."""
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    config = yaml.safe_load(f)
                    if config is None:
                        config = {}
                    return self._merge_configs(default_config, config)
            except Exception as e:
                self.logger.error(f"Error loading YAML config {filepath}: {e}")
        
        # Create default config file
        self._save_yaml_config(filepath, default_config)
        return default_config
    
    def _save_json_config(self, filepath: str, config: Dict):
        """Save configuration to JSON file."""
        try:
            with open(filepath, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving JSON config {filepath}: {e}")
    
    def _save_yaml_config(self, filepath: str, config: Dict):
        """Save configuration to YAML file."""
        try:
            with open(filepath, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving YAML config {filepath}: {e}")
    
    def _merge_configs(self, default: Dict, override: Dict) -> Dict:
        """Recursively merge configuration dictionaries."""
        result = default.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _get_default_game_config(self) -> Dict:
        """Get default game configuration."""
        return {
            "game": {
                "collision_delay": 250,
                "letter_spawn_interval": 60,
                "group_size": 5,
                "level_progress_path": "level_progress.txt"
            },
            "colors": {
                "white": [255, 255, 255],
                "black": [0, 0, 0],
                "flame_colors": [
                    [255, 69, 0],
                    [255, 215, 0],
                    [0, 191, 255]
                ]
            },
            "effects": {
                "laser_effects": [
                    {
                        "colors": [[255, 0, 0], [255, 128, 0]],
                        "widths": [3, 5],
                        "type": "flamethrower"
                    }
                ]
            },
            "sequences": {
                "alphabet": list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
                "numbers": [str(i) for i in range(1, 11)],
                "clcase": list("abcdefghijklmnopqrstuvwxyz"),
                "shapes": ["Circle", "Square", "Triangle", "Rectangle", "Pentagon"],
                "colors": ["Red", "Blue", "Green", "Yellow", "Purple"]
            },
            "game_modes": ["alphabet", "numbers", "clcase", "shapes", "colors"],
            "difficulty": {
                "easy": {
                    "spawn_interval": 90,
                    "collision_delay": 400,
                    "target_speed": 2
                },
                "medium": {
                    "spawn_interval": 60,
                    "collision_delay": 250,
                    "target_speed": 3
                },
                "hard": {
                    "spawn_interval": 40,
                    "collision_delay": 150,
                    "target_speed": 4
                }
            },
            "display": {
                "default_width": 1200,
                "default_height": 800,
                "fullscreen": False,
                "fps": 60
            },
            "audio": {
                "master_volume": 1.0,
                "voice_volume": 0.8,
                "music_volume": 0.3,
                "effects_volume": 0.7
            }
        }
    
    def _get_default_teacher_config(self) -> Dict:
        """Get default teacher customization configuration."""
        return {
            "classroom": {
                "teacher_name": "",
                "class_name": "",
                "school_name": ""
            },
            "content_customization": {
                "enabled_game_modes": ["alphabet", "numbers", "shapes", "colors"],
                "custom_sequences": {
                    "alphabet": {
                        "enabled": True,
                        "custom_letters": [],
                        "focus_letters": []
                    },
                    "numbers": {
                        "enabled": True,
                        "range_start": 1,
                        "range_end": 10,
                        "custom_numbers": []
                    },
                    "shapes": {
                        "enabled": True,
                        "custom_shapes": []
                    },
                    "colors": {
                        "enabled": True,
                        "custom_colors": []
                    }
                }
            },
            "difficulty_settings": {
                "current_difficulty": "medium",
                "allow_student_difficulty_change": True,
                "adaptive_difficulty": False
            },
            "accessibility": {
                "large_font_mode": False,
                "high_contrast": False,
                "colorblind_friendly": False,
                "audio_cues_only": False
            },
            "time_limits": {
                "enabled": False,
                "session_duration_minutes": 15,
                "break_reminders": True
            },
            "rewards": {
                "celebration_sounds": True,
                "visual_feedback": True,
                "progress_tracking": True
            }
        }
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation.
        
        Args:
            key_path: Dot-separated path to the config value (e.g., "game.collision_delay")
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        try:
            keys = key_path.split('.')
            config_type = keys[0]  # 'game' or 'teacher'
            
            if config_type not in self._config_cache:
                return default
            
            value = self._config_cache[config_type]
            for key in keys[1:]:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return default
            
            return value
            
        except Exception as e:
            self.logger.error(f"Error getting config value {key_path}: {e}")
            return default
    
    def set(self, key_path: str, value: Any, save: bool = True):
        """
        Set a configuration value using dot notation.
        
        Args:
            key_path: Dot-separated path to the config value
            value: Value to set
            save: Whether to immediately save to file
        """
        try:
            keys = key_path.split('.')
            config_type = keys[0]  # 'game' or 'teacher'
            
            if config_type not in self._config_cache:
                self.logger.error(f"Invalid config type: {config_type}")
                return
            
            # Navigate to the parent dictionary
            config = self._config_cache[config_type]
            for key in keys[1:-1]:
                if key not in config:
                    config[key] = {}
                config = config[key]
            
            # Set the value
            config[keys[-1]] = value
            
            # Save if requested
            if save:
                self.save_config(config_type)
            
        except Exception as e:
            self.logger.error(f"Error setting config value {key_path}: {e}")
    
    def save_config(self, config_type: str = None):
        """
        Save configuration to files.
        
        Args:
            config_type: Type of config to save ('game' or 'teacher'), or None for all
        """
        try:
            if config_type is None or config_type == 'game':
                self._save_json_config(self.game_config_path, self._config_cache['game'])
            
            if config_type is None or config_type == 'teacher':
                self._save_yaml_config(self.teacher_config_path, self._config_cache['teacher'])
            
            self.logger.info(f"Saved configuration: {config_type or 'all'}")
            
        except Exception as e:
            self.logger.error(f"Error saving configuration: {e}")
    
    def get_legacy_settings(self) -> Dict:
        """
        Get settings in the legacy format for backward compatibility.
        
        Returns:
            Dictionary with legacy setting names
        """
        try:
            return {
                'COLORS_COLLISION_DELAY': self.get('game.game.collision_delay', 250),
                'LEVEL_PROGRESS_PATH': self.get('game.game.level_progress_path', 'level_progress.txt'),
                'WHITE': tuple(self.get('game.colors.white', [255, 255, 255])),
                'BLACK': tuple(self.get('game.colors.black', [0, 0, 0])),
                'FLAME_COLORS': [tuple(color) for color in self.get('game.colors.flame_colors', [[255, 69, 0], [255, 215, 0], [0, 191, 255]])],
                'LASER_EFFECTS': self.get('game.effects.laser_effects', []),
                'LETTER_SPAWN_INTERVAL': self.get('game.game.letter_spawn_interval', 60),
                'SEQUENCES': self.get('game.sequences', {}),
                'GAME_MODES': self.get('game.game_modes', []),
                'GROUP_SIZE': self.get('game.game.group_size', 5)
            }
        except Exception as e:
            self.logger.error(f"Error getting legacy settings: {e}")
            return {}
    
    def is_game_mode_enabled(self, mode: str) -> bool:
        """Check if a game mode is enabled in teacher settings."""
        enabled_modes = self.get('teacher.content_customization.enabled_game_modes', [])
        return mode in enabled_modes
    
    def get_custom_sequence(self, sequence_type: str) -> list:
        """Get customized sequence for a specific type."""
        # Check for teacher customizations first
        custom_config = self.get(f'teacher.content_customization.custom_sequences.{sequence_type}', {})
        
        if custom_config.get('enabled', True):
            # Check for custom content
            if sequence_type == 'alphabet' and custom_config.get('custom_letters'):
                return custom_config['custom_letters']
            elif sequence_type == 'numbers' and custom_config.get('custom_numbers'):
                return custom_config['custom_numbers']
            elif sequence_type in ['shapes', 'colors'] and custom_config.get(f'custom_{sequence_type}'):
                return custom_config[f'custom_{sequence_type}']
            elif sequence_type == 'numbers':
                # Handle number ranges
                start = custom_config.get('range_start', 1)
                end = custom_config.get('range_end', 10)
                return [str(i) for i in range(start, end + 1)]
        
        # Fall back to default sequences
        return self.get(f'game.sequences.{sequence_type}', [])
    
    def get_difficulty_settings(self) -> Dict:
        """Get current difficulty settings."""
        current_difficulty = self.get('teacher.difficulty_settings.current_difficulty', 'medium')
        return self.get(f'game.difficulty.{current_difficulty}', self.get('game.difficulty.medium', {}))
    
    def export_teacher_config(self, filepath: str):
        """Export teacher configuration to a file for sharing."""
        try:
            teacher_config = self._config_cache.get('teacher', {})
            with open(filepath, 'w') as f:
                yaml.dump(teacher_config, f, default_flow_style=False, indent=2)
            self.logger.info(f"Teacher configuration exported to {filepath}")
        except Exception as e:
            self.logger.error(f"Error exporting teacher config: {e}")
    
    def import_teacher_config(self, filepath: str):
        """Import teacher configuration from a file."""
        try:
            with open(filepath, 'r') as f:
                imported_config = yaml.safe_load(f)
            
            if imported_config:
                self._config_cache['teacher'] = self._merge_configs(
                    self._get_default_teacher_config(),
                    imported_config
                )
                self.save_config('teacher')
                self.logger.info(f"Teacher configuration imported from {filepath}")
        except Exception as e:
            self.logger.error(f"Error importing teacher config: {e}")


# Global configuration manager instance
_config_manager = None

def get_config_manager() -> ConfigurationManager:
    """Get the global configuration manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigurationManager()
    return _config_manager

def get_legacy_settings() -> Dict:
    """Get legacy settings for backward compatibility."""
    return get_config_manager().get_legacy_settings()


if __name__ == "__main__":
    # Test the configuration manager
    config = ConfigurationManager()
    
    print("Configuration Manager Test:")
    print("=" * 40)
    
    # Test getting values
    print("Collision delay:", config.get('game.game.collision_delay'))
    print("Flame colors:", config.get('game.colors.flame_colors'))
    print("Game modes:", config.get('game.game_modes'))
    
    # Test teacher settings
    print("Teacher name:", config.get('teacher.classroom.teacher_name'))
    print("Enabled modes:", config.get('teacher.content_customization.enabled_game_modes'))
    
    # Test legacy format
    legacy = config.get_legacy_settings()
    print("Legacy WHITE color:", legacy.get('WHITE'))
    
    print("Configuration system working correctly!")