"""
Base Level Class for SS6 Game
Provides common functionality for all game levels to eliminate duplication.
"""

import math
import random
import pygame
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple, Callable

from settings import (
    BLACK, WHITE, FLAME_COLORS, LETTER_SPAWN_INTERVAL,
    GROUP_SIZE, SEQUENCES
)
from universal_class import (
    GlassShatterManager, HUDManager, MultiTouchManager,
    CheckpointManager, CenterPieceManager, FlamethrowerManager, SoundManager
)


class BaseGameObject:
    """Base class for all game objects (letters, numbers, emojis, etc.)"""

    def __init__(self, x: float, y: float, value: str, obj_type: str = "generic"):
        self.x = x
        self.y = y
        self.value = value
        self.type = obj_type
        self.dx = 0.0
        self.dy = 0.0
        self.size = 240
        self.mass = random.uniform(100, 160)
        self.can_bounce = False
        self.alive = True
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.color = BLACK
        self.surface = None  # For emoji objects

    def update_physics(self, width: int, height: int, bounce_damping: float = 0.8):
        """Update object physics including position and bouncing."""
        self.x += self.dx
        self.y += self.dy

        # Bouncing logic
        if not self.can_bounce and self.y > height // 5:
            self.can_bounce = True

        if self.can_bounce:
            # Left/Right walls
            if self.x <= self.size / 2:
                self.x = self.size / 2
                self.dx = abs(self.dx) * bounce_damping
            elif self.x >= width - self.size / 2:
                self.x = width - self.size / 2
                self.dx = -abs(self.dx) * bounce_damping

            # Top/Bottom walls
            if self.y <= self.size / 2:
                self.y = self.size / 2
                self.dy = abs(self.dy) * bounce_damping
            elif self.y >= height - self.size / 2:
                self.y = height - self.size / 2
                self.dy = -abs(self.dy) * bounce_damping
                # Push horizontally away from edge
                self.dx *= bounce_damping
                if self.x < width / 2:
                    self.dx += random.uniform(0.1, 0.3)
                else:
                    self.dx -= random.uniform(0.1, 0.3)

    def get_rect(self) -> pygame.Rect:
        """Get collision rectangle for the object."""
        return pygame.Rect(
            self.x - self.size / 2,
            self.y - self.size / 2,
            self.size,
            self.size
        )


class BaseLevel(ABC):
    """
    Abstract base class for all game levels.
    Provides common functionality to eliminate code duplication.
    """

    def __init__(
        self,
        width: int,
        height: int,
        screen: pygame.Surface,
        fonts: List[pygame.font.Font],
        small_font: pygame.font.Font,
        target_font: pygame.font.Font,
        particle_manager,
        glass_shatter_manager: GlassShatterManager,
        multi_touch_manager: MultiTouchManager,
        hud_manager: HUDManager,
        checkpoint_manager: CheckpointManager,
        center_piece_manager: CenterPieceManager,
        flamethrower_manager: FlamethrowerManager,
        resource_manager,
        create_explosion_func: Callable,
        create_flame_effect_func: Callable,
        apply_explosion_effect_func: Callable,
        create_particle_func: Callable,
        explosions_list: List[Dict],
        lasers_list: List[Dict],
        draw_explosion_func: Callable,
        game_over_screen_func: Callable,
        sound_manager: SoundManager,
    ):
        """
        Initialize the base level with common components.

        Args:
            width, height: Screen dimensions
            screen: Pygame screen surface
            fonts: List of font objects
            small_font: Small font for UI
            target_font: Font for target objects
            particle_manager: Particle system manager
            glass_shatter_manager: Glass shatter effects
            multi_touch_manager: Touch input manager
            hud_manager: HUD display manager
            checkpoint_manager: Checkpoint system
            center_piece_manager: Center piece manager
            flamethrower_manager: Flamethrower effects
            resource_manager: Resource caching manager
            create_explosion_func: Function to create explosions
            create_flame_effect_func: Function to create flame effects
            apply_explosion_effect_func: Function to apply explosion physics
            create_particle_func: Function to create particles
            explosions_list: Global explosions list
            lasers_list: Global lasers list
            draw_explosion_func: Function to draw explosions
            game_over_screen_func: Function to show game over screen
            sound_manager: Sound system manager
        """
        # Core components
        self.width = width
        self.height = height
        self.screen = screen
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

        # Function references
        self.create_explosion = create_explosion_func
        self.create_flame_effect = create_flame_effect_func
        self.apply_explosion_effect = apply_explosion_effect_func
        self.create_particle = create_particle_func
        self.explosions = explosions_list
        self.lasers = lasers_list
        self.draw_explosion = draw_explosion_func
        self.game_over_screen = game_over_screen_func

        # Game state
        self.reset_game_state()

        # Background stars
        self.stars = self._create_background_stars()

    def reset_game_state(self):
        """Reset common game state variables."""
        # Group progression
        self.current_group_index = 0
        self.current_group = []
        self.target_object = None
        self.objects_to_target = []

        # Counters
        self.total_destroyed = 0
        self.overall_destroyed = 0
        self.objects_spawned = 0
        self.objects_destroyed = 0
        self.last_checkpoint_triggered = 0
        self.score = 0

        # Game flow
        self.running = True
        self.game_started = False
        self.game_objects = []
        self.objects_to_spawn = []
        self.frame_count = 0

        # Checkpoint system
        self.checkpoint_waiting = False
        self.checkpoint_delay_frames = 0
        self.just_completed_level = False

        # Input state
        self.last_click_time = 0
        self.player_x = self.width // 2
        self.player_y = self.height // 2
        self.click_cooldown = 0
        self.mouse_down = False
        self.mouse_press_time = 0
        self.click_count = 0

        # Abilities
        self.abilities = ["laser", "aoe", "charge_up"]
        self.current_ability = "laser"

    def _create_background_stars(self) -> List[List]:
        """Create background stars for the level."""
        stars = []
        for _ in range(100):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            radius = random.randint(2, 4)
            stars.append([x, y, radius])
        return stars

    def _handle_common_events(self) -> Optional[str]:
        """Handle common pygame events. Returns 'menu' if should exit to menu."""
        for event in pygame.event.get():
            # Handle glass shatter events first
            self.glass_shatter_manager.handle_event(event)

            if event.type == pygame.QUIT:
                self.running = False
                return None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "menu"  # Return to level menu
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
                if duration <= 1000:  # Click (not hold)
                    self.click_count += 1
                    if not self.game_started:
                        self.game_started = True
                    else:
                        click_x, click_y = pygame.mouse.get_pos()
                        self._handle_click(click_x, click_y)

            elif event.type == pygame.FINGERDOWN:
                touch_result = self.multi_touch_manager.handle_touch_down(event)
                if touch_result is None:
                    continue
                touch_id, touch_x, touch_y = touch_result
                if not self.game_started:
                    self.game_started = True
                else:
                    self._handle_click(touch_x, touch_y)

            elif event.type == pygame.FINGERUP:
                touch_result = self.multi_touch_manager.handle_touch_up(event)
                if touch_result is not None:
                    touch_id, last_x, last_y = touch_result

        return None

    def _handle_click(self, x: float, y: float) -> bool:
        """
        Handle click/touch at given coordinates.
        Returns True if target was hit, False otherwise.
        """
        hit_target = False

        # Process click on game objects
        for obj in self.game_objects[:]:
            if obj.get_rect().collidepoint(x, y):
                hit_target = self._process_object_hit(obj, x, y)
                if hit_target:
                    break

        # Handle miss
        if not hit_target and self.game_started:
            self.glass_shatter_manager.handle_misclick(x, y)

        return hit_target

    def _process_object_hit(self, obj: BaseGameObject, x: float, y: float) -> bool:
        """
        Process hitting a game object.
        Returns True if object was destroyed, False otherwise.
        """
        # Check if this object should be destroyed
        if self._should_destroy_object(obj):
            # Play voice sound if applicable
            if hasattr(self.sound_manager, 'play_voice') and obj.value:
                try:
                    self.sound_manager.play_voice(str(obj.value))
                except:
                    pass  # Ignore sound errors

            # Create destruction effects
            self._create_destruction_effects(obj)

            # Remove object
            if obj in self.game_objects:
                self.game_objects.remove(obj)
                self.objects_destroyed += 1

            return True
        return False

    def _should_destroy_object(self, obj: BaseGameObject) -> bool:
        """Override in subclasses to define hit conditions."""
        return True  # Default: any hit destroys

    def _create_destruction_effects(self, obj: BaseGameObject):
        """Create common destruction effects."""
        # Explosion
        self.create_explosion(obj.x, obj.y)

        # Flame effect
        self.create_flame_effect(self.player_x, self.player_y - 80, obj.x, obj.y)

        # Convergence effect
        self.center_piece_manager.trigger_convergence(obj.x, obj.y)

        # Explosion physics
        self.apply_explosion_effect(obj.x, obj.y, 150, self.game_objects)

        # Particles
        for _ in range(20):
            self.create_particle(
                obj.x, obj.y,
                random.choice(FLAME_COLORS),
                random.randint(40, 80),
                random.uniform(-2, 2),
                random.uniform(-2, 2),
                20
            )

    def _spawn_objects(self):
        """Spawn game objects at regular intervals."""
        if self.objects_to_spawn and self.frame_count % LETTER_SPAWN_INTERVAL == 0:
            obj_data = self.objects_to_spawn.pop(0)
            obj = self._create_game_object(obj_data)
            if obj:
                self.game_objects.append(obj)
                self.objects_spawned += 1

    def _create_game_object(self, obj_data: Dict[str, Any]) -> Optional[BaseGameObject]:
        """Create a game object from data. Override in subclasses."""
        return None

    def _update_objects(self):
        """Update all game objects physics."""
        for obj in self.game_objects[:]:
            obj.update_physics(self.width, self.height)
            if not obj.alive:
                self.game_objects.remove(obj)

    def _handle_checkpoint_logic(self):
        """Handle checkpoint display logic."""
        self.overall_destroyed = self.total_destroyed + self.objects_destroyed

        if self.checkpoint_waiting:
            if self.checkpoint_delay_frames <= 0:
                self.checkpoint_waiting = False
                if not self.checkpoint_manager.show_checkpoint_screen(self.screen, self.get_mode_name()):
                    self.running = False
                else:
                    self.game_started = True
            else:
                self.checkpoint_delay_frames -= 1

        elif (
            self.overall_destroyed > 0
            and self.overall_destroyed % 10 == 0
            and self.overall_destroyed // 10 > self.last_checkpoint_triggered
            and not self.just_completed_level
        ):
            self.last_checkpoint_triggered = self.overall_destroyed // 10
            self.checkpoint_waiting = True
            self.checkpoint_delay_frames = 60

    def _handle_level_progression(self) -> Optional[bool]:
        """Handle level progression. Returns None to continue, False to exit."""
        # Check if current group is finished
        if not self.game_objects and not self.objects_to_spawn and not self.objects_to_target:
            self.total_destroyed += self.objects_destroyed
            self.current_group_index += 1
            self.just_completed_level = True

            if self.current_group_index < len(self.get_groups()):
                self._start_next_group()
            else:
                return self._handle_level_complete()

        return None

    def _start_next_group(self):
        """Start the next group."""
        self.current_group = self.get_groups()[self.current_group_index]
        self.objects_to_spawn = self.current_group.copy()
        self.objects_to_target = self.current_group.copy()

        if self.objects_to_target:
            self.target_object = self.objects_to_target[0]
            self._setup_target_tracking()

        # Reset counters
        self.objects_destroyed = 0
        self.objects_spawned = 0
        self.just_completed_level = False
        self.game_started = True
        self.last_checkpoint_triggered = self.overall_destroyed // 10

    def _handle_level_complete(self) -> bool:
        """Handle level completion. Returns False to exit to menu."""
        pygame.time.delay(500)
        if not self.checkpoint_manager.show_checkpoint_screen(self.screen, self.get_mode_name()):
            self.running = False
            return False
        return False

    def _draw_common_frame(self, stars: List[List]):
        """Draw common frame elements."""
        # Update glass shatter manager
        self.glass_shatter_manager.update()

        # Apply screen shake
        offset_x, offset_y = self.glass_shatter_manager.get_screen_shake_offset()

        # Fill background
        self.screen.fill(self.glass_shatter_manager.get_background_color())

        # Draw cracks
        self.glass_shatter_manager.draw_cracks(self.screen)

        # Draw stars
        self._draw_stars(stars, offset_x, offset_y)

        # Draw center piece
        self.center_piece_manager.update_and_draw(
            self.screen, self.target_object, self.get_mode_name(), offset_x, offset_y
        )

        # Draw game objects
        self._draw_game_objects(offset_x, offset_y)

        # Draw effects
        self._draw_effects(offset_x, offset_y)

        # Draw HUD
        self._draw_hud()

    def _draw_stars(self, stars: List[List], offset_x: float, offset_y: float):
        """Draw and update background stars."""
        for star in stars:
            x, y, radius = star
            y += 1
            pygame.draw.circle(self.screen, (200, 200, 200), (x + offset_x, y + offset_y), radius)
            if y > self.height + radius:
                y = random.randint(-50, -10)
                x = random.randint(0, self.width)
            star[1] = y
            star[0] = x

    def _draw_game_objects(self, offset_x: float, offset_y: float):
        """Draw all game objects. Override in subclasses for specific rendering."""
        pass

    def _draw_effects(self, offset_x: float, offset_y: float):
        """Draw all effects (explosions, lasers, etc.)."""
        # Flamethrower effects
        self.flamethrower_manager.update()
        self.flamethrower_manager.draw(self.screen, offset_x, offset_y)

        # Legacy lasers
        self._process_lasers(offset_x, offset_y)

        # Explosions
        self._process_explosions(offset_x, offset_y)

    def _process_lasers(self, offset_x: float, offset_y: float):
        """Process legacy laser effects."""
        for laser in self.lasers[:]:
            if laser["duration"] > 0:
                if laser["type"] != "flamethrower":
                    pygame.draw.line(
                        self.screen,
                        random.choice(laser.get("colors", FLAME_COLORS)),
                        (laser["start_pos"][0] + offset_x, laser["start_pos"][1] + offset_y),
                        (laser["end_pos"][0] + offset_x, laser["end_pos"][1] + offset_y),
                        random.choice(laser.get("widths", [5, 10, 15])),
                    )
                laser["duration"] -= 1
            else:
                self.lasers.remove(laser)

    def _process_explosions(self, offset_x: float, offset_y: float):
        """Process explosion effects."""
        for explosion in self.explosions[:]:
            if explosion["duration"] > 0:
                self.draw_explosion(explosion, offset_x, offset_y)
                explosion["duration"] -= 1
            else:
                self.explosions.remove(explosion)

    def _draw_hud(self):
        """Draw HUD elements."""
        self.hud_manager.display_info(
            self.screen,
            self.score,
            self.current_ability,
            self.target_object,
            self.overall_destroyed,
            self.get_total_objects(),
            self.get_mode_name(),
        )

    # Abstract methods that subclasses must implement
    @abstractmethod
    def get_mode_name(self) -> str:
        """Return the mode name for this level."""
        pass

    @abstractmethod
    def get_groups(self) -> List[List]:
        """Return the groups for this level."""
        pass

    @abstractmethod
    def get_total_objects(self) -> int:
        """Return the total number of objects in this level."""
        pass

    @abstractmethod
    def _setup_target_tracking(self):
        """Setup target tracking for the current target."""
        pass

    def run(self) -> bool:
        """
        Main game loop. Override in subclasses for level-specific logic.
        Returns False to exit to menu.
        """
        clock = pygame.time.Clock()

        while self.running:
            # Handle events
            event_result = self._handle_common_events()
            if event_result == "menu":
                return False

            # Level-specific updates
            if self.game_started:
                self._spawn_objects()
                self._update_objects()

            # Common updates
            self._handle_checkpoint_logic()
            progression_result = self._handle_level_progression()
            if progression_result is not None:
                return progression_result

            # Draw frame
            self._draw_common_frame(self.stars)

            # Update frame counter and display
            self.frame_count += 1
            pygame.display.flip()
            clock.tick(50)

        return False
