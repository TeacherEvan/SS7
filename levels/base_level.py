"""
Base Level Class for SS6 Game

This module provides a base class that contains common functionality shared
across all game levels, reducing code duplication and improving maintainability.
"""

import math
import random
import pygame
from abc import ABC, abstractmethod

from settings import (
    BLACK,
    FLAME_COLORS,
    GROUP_SIZE,
    LETTER_SPAWN_INTERVAL,
    LEVEL_PROGRESS_PATH,
    SEQUENCES,
    WHITE,
)


class BaseLevel(ABC):
    """
    Abstract base class for all game levels.
    Contains common functionality like stars initialization, event handling,
    and main game loop structure.
    """

    def __init__(
        self,
        width,
        height,
        screen,
        fonts,
        small_font,
        target_font,
        particle_manager,
        glass_shatter_manager,
        multi_touch_manager,
        hud_manager,
        checkpoint_manager,
        center_piece_manager,
        flamethrower_manager,
        resource_manager,
        create_explosion_func,
        create_flame_effect_func,
        apply_explosion_effect_func,
        create_particle_func,
        explosions_list,
        lasers_list,
        draw_explosion_func,
        game_over_screen_func,
        sound_manager,
    ):
        """Initialize base level with common parameters."""
        # Screen and display
        self.width = width
        self.height = height
        self.screen = screen
        
        # Fonts
        self.fonts = fonts
        self.small_font = small_font
        self.target_font = target_font
        
        # Managers
        self.particle_manager = particle_manager
        self.glass_shatter_manager = glass_shatter_manager
        self.multi_touch_manager = multi_touch_manager
        self.hud_manager = hud_manager
        self.checkpoint_manager = checkpoint_manager
        self.center_piece_manager = center_piece_manager
        self.flamethrower_manager = flamethrower_manager
        self.resource_manager = resource_manager
        self.sound_manager = sound_manager
        
        # Effect functions
        self.create_explosion = create_explosion_func
        self.create_flame_effect = create_flame_effect_func
        self.apply_explosion_effect = apply_explosion_effect_func
        self.create_particle = create_particle_func
        self.draw_explosion = draw_explosion_func
        self.game_over_screen = game_over_screen_func
        
        # Global lists
        self.explosions = explosions_list
        self.lasers = lasers_list
        
        # Common game state
        self.running = True
        self.game_started = False
        self.frame_count = 0
        
        # Common input state
        self.mouse_down = False
        self.mouse_press_time = 0
        self.click_count = 0
        self.abilities = ["laser", "aoe", "charge_up"]
        self.current_ability = "laser"
        
        # Initialize background stars once
        self.stars = self._create_background_stars()

    def _create_background_stars(self):
        """Create background stars - common to all levels."""
        stars = []
        for _ in range(100):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            radius = random.randint(2, 4)
            stars.append([x, y, radius])
        return stars

    def _draw_stars(self, offset_x=0, offset_y=0):
        """Draw and update background stars."""
        for star in self.stars:
            x, y, radius = star
            y += 1  # Slower star movement speed
            pygame.draw.circle(
                self.screen, (200, 200, 200), (x + offset_x, y + offset_y), radius
            )
            if y > self.height + radius:
                y = random.randint(-50, -10)
                x = random.randint(0, self.width)
            star[1] = y
            star[0] = x

    def _handle_common_events(self, event):
        """Handle common events across all levels."""
        # Handle glass shatter events first
        self.glass_shatter_manager.handle_event(event)

        if event.type == pygame.QUIT:
            self.running = False
            return False
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Return to level menu instead of exiting the game completely
                self.running = False
                return "menu"
            if event.key == pygame.K_SPACE:
                self.current_ability = self.abilities[
                    (self.abilities.index(self.current_ability) + 1) % len(self.abilities)
                ]

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not self.mouse_down:
                self.mouse_press_time = pygame.time.get_ticks()
                self.mouse_down = True

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            release_time = pygame.time.get_ticks()
            self.mouse_down = False
            duration = release_time - self.mouse_press_time
            if duration <= 1000:  # Check if it's a click (not a hold)
                self.click_count += 1
                if not self.game_started:
                    self.game_started = True
                else:
                    click_x, click_y = pygame.mouse.get_pos()
                    self._handle_click(click_x, click_y)
        
        return True

    def reset_level_state(self):
        """Reset level state - should be overridden by subclasses."""
        self.running = True
        self.game_started = False
        self.frame_count = 0
        self.mouse_down = False
        self.mouse_press_time = 0
        self.click_count = 0
        
        # Reset managers
        if self.particle_manager:
            self.particle_manager.reset()
        if self.glass_shatter_manager:
            self.glass_shatter_manager.reset()
        if self.multi_touch_manager:
            self.multi_touch_manager.reset()
        if self.checkpoint_manager:
            self.checkpoint_manager.reset()
        if self.center_piece_manager:
            self.center_piece_manager.reset()
        if self.flamethrower_manager:
            self.flamethrower_manager.reset()

    def run(self):
        """
        Main entry point to run the level.
        Template method that calls abstract methods for level-specific logic.
        """
        self.reset_level_state()
        
        # Main game loop
        clock = pygame.time.Clock()
        
        while self.running:
            # Handle events
            if not self._handle_events():
                return False
                
            # Level-specific updates
            if self.game_started:
                self._update_level_logic()
                
            # Level-specific rendering
            self._draw_frame()
            
            # Level-specific progression logic
            progression_result = self._handle_level_progression()
            if progression_result is not None:
                return progression_result
                
            # Update frame counter and display
            self.frame_count += 1
            pygame.display.flip()
            clock.tick(50)
            
        return False

    @abstractmethod
    def _handle_events(self):
        """Handle level-specific events. Must be implemented by subclasses."""
        pass

    @abstractmethod
    def _update_level_logic(self):
        """Update level-specific game logic. Must be implemented by subclasses."""
        pass

    @abstractmethod
    def _draw_frame(self):
        """Draw level-specific frame. Must be implemented by subclasses."""
        pass

    @abstractmethod
    def _handle_level_progression(self):
        """Handle level-specific progression logic. Must be implemented by subclasses."""
        pass

    @abstractmethod
    def _handle_click(self, x, y):
        """Handle level-specific click logic. Must be implemented by subclasses."""
        pass