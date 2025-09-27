"""
Game State Manager for SS6

This module provides centralized management of global game state,
reducing global variable pollution and ensuring proper cleanup between levels.
"""

import pygame
from typing import List, Dict, Any, Optional


class GameStateManager:
    """
    Centralized manager for global game state.
    Handles explosions, lasers, particles, and other shared state.
    """
    
    def __init__(self):
        """Initialize the game state manager."""
        self.explosions: List[Dict[str, Any]] = []
        self.lasers: List[Dict[str, Any]] = []
        self.particles: List[Dict[str, Any]] = []
        
        # Charge-up effect state
        self.charging_ability = False
        self.charge_timer = 0
        self.charge_particles: List[Dict[str, Any]] = []
        self.ability_target = None
        
        # Swirl particles state
        self.swirl_particles: List[Dict[str, Any]] = []
        self.particles_converging = False
        self.convergence_target = None
        self.convergence_timer = 0
        
        # Player state
        self.player_color_transition = 0
        self.player_current_color = None
        self.player_next_color = None
        
        # Screen shake state
        self.shake_duration = 0
        self.shake_magnitude = 0

    def reset_all_state(self):
        """Reset all global state - call between levels."""
        self.explosions.clear()
        self.lasers.clear()
        self.particles.clear()
        self.charge_particles.clear()
        self.swirl_particles.clear()
        
        # Reset flags and counters
        self.charging_ability = False
        self.charge_timer = 0
        self.ability_target = None
        self.particles_converging = False
        self.convergence_target = None
        self.convergence_timer = 0
        self.player_color_transition = 0
        self.shake_duration = 0
        self.shake_magnitude = 0

    def reset_effects_state(self):
        """Reset only effect-related state (lighter reset for performance)."""
        self.explosions.clear()
        self.lasers.clear()
        
        # Reset charge-up state
        self.charging_ability = False
        self.charge_timer = 0
        self.charge_particles.clear()
        self.ability_target = None
        
        # Reset swirl state
        self.particles_converging = False
        self.convergence_target = None
        self.convergence_timer = 0

    def get_explosions(self) -> List[Dict[str, Any]]:
        """Get the explosions list."""
        return self.explosions

    def get_lasers(self) -> List[Dict[str, Any]]:
        """Get the lasers list."""
        return self.lasers

    def get_particles(self) -> List[Dict[str, Any]]:
        """Get the particles list."""
        return self.particles

    def add_explosion(self, explosion_data: Dict[str, Any]):
        """Add an explosion to the state."""
        self.explosions.append(explosion_data)

    def add_laser(self, laser_data: Dict[str, Any]):
        """Add a laser to the state."""
        self.lasers.append(laser_data)

    def add_particle(self, particle_data: Dict[str, Any]):
        """Add a particle to the state."""
        self.particles.append(particle_data)

    def update_explosions(self):
        """Update all explosions and remove dead ones."""
        active_explosions = []
        for explosion in self.explosions:
            if explosion.get('duration', 0) > 0:
                explosion['duration'] -= 1
                active_explosions.append(explosion)
        self.explosions = active_explosions

    def update_lasers(self):
        """Update all lasers and remove dead ones."""
        active_lasers = []
        for laser in self.lasers:
            if laser.get('duration', 0) > 0:
                laser['duration'] -= 1
                active_lasers.append(laser)
        self.lasers = active_lasers

    def update_particles(self):
        """Update all particles and remove dead ones."""
        active_particles = []
        for particle in self.particles:
            if particle.get('life', 0) > 0:
                particle['life'] -= 1
                # Update position
                particle['x'] += particle.get('dx', 0)
                particle['y'] += particle.get('dy', 0)
                active_particles.append(particle)
        self.particles = active_particles

    def update_all_effects(self):
        """Update all effects in one call for performance."""
        self.update_explosions()
        self.update_lasers()
        self.update_particles()

    def get_effect_counts(self) -> Dict[str, int]:
        """Get count of active effects for debugging/monitoring."""
        return {
            'explosions': len(self.explosions),
            'lasers': len(self.lasers),
            'particles': len(self.particles),
        }

    def is_charging(self) -> bool:
        """Check if ability charging is active."""
        return self.charging_ability

    def start_charging(self, target=None):
        """Start ability charging."""
        self.charging_ability = True
        self.charge_timer = 0
        self.ability_target = target

    def stop_charging(self):
        """Stop ability charging."""
        self.charging_ability = False
        self.charge_timer = 0
        self.charge_particles.clear()
        self.ability_target = None

    def update_charging(self):
        """Update charging state."""
        if self.charging_ability:
            self.charge_timer += 1

    def set_screen_shake(self, duration: int, magnitude: float):
        """Set screen shake effect."""
        self.shake_duration = duration
        self.shake_magnitude = magnitude

    def update_screen_shake(self):
        """Update screen shake effect."""
        if self.shake_duration > 0:
            self.shake_duration -= 1
            if self.shake_duration <= 0:
                self.shake_magnitude = 0

    def get_screen_shake_offset(self) -> tuple:
        """Get current screen shake offset."""
        if self.shake_duration > 0:
            import random
            offset_x = random.randint(-int(self.shake_magnitude), int(self.shake_magnitude))
            offset_y = random.randint(-int(self.shake_magnitude), int(self.shake_magnitude))
            return offset_x, offset_y
        return 0, 0


# Global state manager instance
_game_state_manager = None

def get_game_state_manager() -> GameStateManager:
    """Get the global game state manager instance."""
    global _game_state_manager
    if _game_state_manager is None:
        _game_state_manager = GameStateManager()
    return _game_state_manager

def reset_global_game_state():
    """Reset all global game state - call between levels."""
    manager = get_game_state_manager()
    manager.reset_all_state()