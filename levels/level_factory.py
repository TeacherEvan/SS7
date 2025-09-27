"""
Level Factory for SS6 Game

This module provides a factory class for creating and managing game levels
with proper state isolation and resource management.
"""

from levels.alphabet_level import AlphabetLevel
from levels.numbers_level import NumbersLevel
from levels.cl_case_level import CLCaseLevel
from levels.colors_level import ColorsLevel
from levels.shapes_level import ShapesLevel


class LevelFactory:
    """
    Factory class for creating game levels with proper state management.
    Ensures each level is loaded individually without state bleeding.
    """
    
    def __init__(self):
        """Initialize the level factory."""
        self._level_cache = {}
        self._current_level = None

    def create_level(self, mode, **kwargs):
        """
        Create a level instance with proper state isolation.
        
        Args:
            mode (str): The game mode ('alphabet', 'numbers', etc.)
            **kwargs: Level initialization parameters
            
        Returns:
            BaseLevel: The created level instance
        """
        # Clear any existing level state first
        self._cleanup_current_level()
        
        # Create level based on mode
        level_classes = {
            'alphabet': AlphabetLevel,
            'numbers': NumbersLevel,
            'clcase': CLCaseLevel,
            'colors': ColorsLevel,
            'shapes': ShapesLevel,
        }
        
        if mode not in level_classes:
            raise ValueError(f"Unknown game mode: {mode}")
            
        level_class = level_classes[mode]
        
        # Create the level with provided parameters
        level = level_class(**kwargs)
        
        # Store reference to current level
        self._current_level = level
        
        return level

    def _cleanup_current_level(self):
        """Clean up the current level to prevent state bleeding."""
        if self._current_level:
            # Reset level state
            if hasattr(self._current_level, 'reset_level_state'):
                self._current_level.reset_level_state()
            
            # Clear references
            self._current_level = None

    def reset_global_state(self, explosions_list, lasers_list, particle_manager):
        """
        Reset global state that might persist between levels.
        
        Args:
            explosions_list: Global explosions list to clear
            lasers_list: Global lasers list to clear
            particle_manager: Particle manager to reset
        """
        # Clear global effect lists
        if explosions_list:
            explosions_list.clear()
        if lasers_list:
            lasers_list.clear()
            
        # Reset particle manager
        if particle_manager:
            particle_manager.reset()

    def get_level_parameters(self, mode, width, height, screen, fonts, small_font, 
                           target_font, particle_manager, glass_shatter_manager,
                           multi_touch_manager, hud_manager, checkpoint_manager,
                           center_piece_manager, flamethrower_manager, resource_manager,
                           create_explosion_func, create_flame_effect_func,
                           apply_explosion_effect_func, create_particle_func,
                           explosions_list, lasers_list, draw_explosion_func,
                           game_over_screen_func, sound_manager):
        """
        Get the standardized parameter dictionary for level creation.
        This reduces the massive parameter passing problem.
        """
        return {
            'width': width,
            'height': height,
            'screen': screen,
            'fonts': fonts,
            'small_font': small_font,
            'target_font': target_font,
            'particle_manager': particle_manager,
            'glass_shatter_manager': glass_shatter_manager,
            'multi_touch_manager': multi_touch_manager,
            'hud_manager': hud_manager,
            'checkpoint_manager': checkpoint_manager,
            'center_piece_manager': center_piece_manager,
            'flamethrower_manager': flamethrower_manager,
            'resource_manager': resource_manager,
            'create_explosion_func': create_explosion_func,
            'create_flame_effect_func': create_flame_effect_func,
            'apply_explosion_effect_func': apply_explosion_effect_func,
            'create_particle_func': create_particle_func,
            'explosions_list': explosions_list,
            'lasers_list': lasers_list,
            'draw_explosion_func': draw_explosion_func,
            'game_over_screen_func': game_over_screen_func,
            'sound_manager': sound_manager,
        }


# Global factory instance
_level_factory = None

def get_level_factory():
    """Get the global level factory instance."""
    global _level_factory
    if _level_factory is None:
        _level_factory = LevelFactory()
    return _level_factory