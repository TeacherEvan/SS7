import math
import random
import pygame
from typing import List, Dict, Any

from settings import (
    BLACK,
    FLAME_COLORS,
    GROUP_SIZE,
    LETTER_SPAWN_INTERVAL,
    LEVEL_PROGRESS_PATH,
    SEQUENCES,
    WHITE,
)
from base_level import BaseLevel
from unified_physics import UnifiedObjectFactory, UnifiedTargetSystem, UnifiedPhysicsSystem
from universal_class import (
    CenterPieceManager,
    CheckpointManager,
    FlamethrowerManager,
    GlassShatterManager,
    HUDManager,
    MultiTouchManager,
)


class AlphabetLevel(BaseLevel):
    """
    Handles the Alphabet (ABC) level gameplay logic.
    Sequential letter targeting through the alphabet A-Z.
    Now inherits from BaseLevel to eliminate code duplication.
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
        """
        Initialize the Alphabet level using BaseLevel.

        Args:
            width (int): Screen width
            height (int): Screen height
            screen: Pygame screen surface
            fonts: List of pygame font objects
            small_font: Small font for UI text
            target_font: Font for target letters
            particle_manager: Particle system manager
            glass_shatter_manager: Glass shatter effect manager
            multi_touch_manager: Multi-touch input manager
            hud_manager: HUD display manager
            checkpoint_manager: Checkpoint screen manager
            center_piece_manager: Center piece swirl manager
            flamethrower_manager: Flamethrower effect manager
            resource_manager: Resource caching manager
            create_explosion_func: Function to create explosion effects
            create_flame_effect_func: Function to create flame effects
            apply_explosion_effect_func: Function to apply explosion push effects
            create_particle_func: Function to create individual particles
            explosions_list: Reference to the global explosions list
            lasers_list: Reference to the global lasers list
            draw_explosion_func: Function to draw explosion effects
            game_over_screen_func: Function to show game over screen
            sound_manager: Sound effect manager
        """
        # Initialize base level (eliminates ~100 lines of duplicate initialization)
        super().__init__(
            width, height, screen, fonts, small_font, target_font,
            particle_manager, glass_shatter_manager, multi_touch_manager,
            hud_manager, checkpoint_manager, center_piece_manager,
            flamethrower_manager, resource_manager, create_explosion_func,
            create_flame_effect_func, apply_explosion_effect_func,
            create_particle_func, explosions_list, lasers_list,
            draw_explosion_func, game_over_screen_func, sound_manager
        )

        # Get event manager for tracking
        try:
            from utils.event_tracker import get_event_manager
            self.event_manager = get_event_manager()
        except ImportError:
            self.event_manager = None

        # Initialize unified systems
        self.object_factory = UnifiedObjectFactory(resource_manager)
        self.target_system = UnifiedTargetSystem()
        self.physics_system = UnifiedPhysicsSystem(width, height)

        # Alphabet-specific configuration
        self.sequence = SEQUENCES["alphabet"]
        self.groups = [
            self.sequence[i : i + GROUP_SIZE] for i in range(0, len(self.sequence), GROUP_SIZE)
        ]
        self.TOTAL_LETTERS = len(self.sequence)

        # Alphabet-specific game objects (using new system)
        self.game_objects = []  # Override base class to use BaseGameObject
        self.letters = []  # Keep for backward compatibility during transition

        # Reset to initialize alphabet-specific state
        self.reset_level_state()

    def reset_level_state(self):
        """Reset all level-specific state variables."""
        # Group progression variables
        self.current_group_index = 0
        self.current_group = self.groups[self.current_group_index] if self.groups else []
        self.letters_to_target = self.current_group.copy()
        self.target_letter = self.letters_to_target[0] if self.letters_to_target else None

        # Counters and tracking
        self.total_destroyed = 0
        self.overall_destroyed = 0
        self.letters_spawned = 0
        self.letters_destroyed = 0
        self.last_checkpoint_triggered = 0
        self.score = 0

        # Game state
        self.running = True
        self.game_started = False
        self.letters = []
        self.letters_to_spawn = self.current_group.copy()
        self.frame_count = 0

        # Checkpoint state
        self.checkpoint_waiting = False
        self.checkpoint_delay_frames = 0
        self.just_completed_level = False

        # Input state
        self.last_click_time = 0
        self.player_x = self.width // 2
        self.player_y = self.height // 2
        self.player_color_index = 0
        self.click_cooldown = 0
        self.mouse_down = False
        self.mouse_press_time = 0
        self.click_count = 0

        # Emoji completion tracking (any order)
        self.current_target_hits = (
            set()
        )  # Track what's been hit for current target {letter, emoji1, emoji2}
        self.targets_needed = set()  # What needs to be hit for current target completion

        # Initialize target tracking for first letter
        if self.target_letter:
            self._reset_target_tracking(self.target_letter)

        # Abilities (maintained for compatibility)
        self.abilities = ["laser", "aoe", "charge_up"]
        self.current_ability = "laser"

    def run(self):
        """
        Main entry point to run the alphabet level.

        Returns:
            bool: False to return to menu, True to restart level
        """
        self.reset_level_state()

        # Initialize background stars
        stars = []
        for _ in range(100):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            radius = random.randint(2, 4)
            stars.append([x, y, radius])

        # Main game loop
        clock = pygame.time.Clock()

        while self.running:
            # Handle events
            if not self._handle_events():
                return False

            # Spawn letters
            if self.game_started:
                self._spawn_letters()

            # Update physics and collisions
            self._update_letters()

            # Handle checkpoint logic
            self._handle_checkpoint_logic()

            # Handle level progression
            progression_result = self._handle_level_progression()
            if progression_result is not None:
                return progression_result

            # Draw frame
            self._draw_frame(stars)

            # Update frame counter and display
            self.frame_count += 1
            pygame.display.flip()
            fps = clock.tick(50)

            # Track performance metrics
            if self.event_manager and self.frame_count % 30 == 0:  # Track every 30 frames
                self.event_manager.get_tracker("performance").track_frame(fps)

        return False

    def _handle_events(self):
        """Handle all pygame events."""
        for event in pygame.event.get():
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
                        current_time = release_time
                        self.last_click_time = current_time

                        # Flag to track if click hit a target
                        hit_target = False

                        # Process Click on Target (letters and emojis)
                        for obj in self.letters[:]:
                            if obj["rect"].collidepoint(click_x, click_y):
                                hit_target = True

                                # Check if this object is part of current target
                                obj_id = obj["value"]
                                if (
                                    obj_id in self.targets_needed
                                    and obj_id not in self.current_target_hits
                                ):
                                    # Hit a valid target!
                                    self.current_target_hits.add(obj_id)
                                    self.score += 10

                                    # Play voice sound for letters
                                    if obj.get("type") == "letter" and self.sound_manager:
                                        self.sound_manager.play_voice(obj["value"])

                                    # Common destruction effects
                                    self.create_explosion(obj["x"], obj["y"])
                                    self.create_flame_effect(
                                        self.player_x, self.player_y - 80, obj["x"], obj["y"]
                                    )
                                    self.center_piece_manager.trigger_convergence(
                                        obj["x"], obj["y"]
                                    )
                                    self.apply_explosion_effect(
                                        obj["x"], obj["y"], 150, self.letters
                                    )

                                    # Add visual feedback particles
                                    for i in range(20):
                                        self.create_particle(
                                            obj["x"],
                                            obj["y"],
                                            random.choice(FLAME_COLORS),
                                            random.randint(40, 80),
                                            random.uniform(-2, 2),
                                            random.uniform(-2, 2),
                                            20,
                                        )

                                    # Remove object and update counts
                                    self.letters.remove(obj)
                                    self.letters_destroyed += 1

                                    # Track target hit event
                                    if self.event_manager:
                                        self.event_manager.get_tracker("gameplay").track_target_hit(
                                            obj.get("type", "unknown"), obj_id, 10
                                        )

                                    # Check if target is complete (letter + both emojis hit)
                                    if self.current_target_hits == self.targets_needed:
                                        self._complete_current_target()

                                    break  # Exit loop after processing one hit

                        # If no target was hit, add a crack to the screen
                        if not hit_target and self.game_started:
                            self.glass_shatter_manager.handle_misclick(click_x, click_y)

                            # Track missed target event
                            if self.event_manager:
                                self.event_manager.get_tracker("gameplay").track_target_missed(
                                    click_x, click_y
                                )

            elif event.type == pygame.FINGERDOWN:
                touch_result = self.multi_touch_manager.handle_touch_down(event)
                if touch_result is None:
                    continue  # Touch was ignored due to cooldown
                touch_id, touch_x, touch_y = touch_result
                if not self.game_started:
                    self.game_started = True
                else:
                    # Flag to track if touch hit a target
                    hit_target = False

                    # Process Touch on Target (letters and emojis)
                    for obj in self.letters[:]:
                        if obj["rect"].collidepoint(touch_x, touch_y):
                            hit_target = True

                            # Check if this object is part of current target
                            obj_id = obj["value"]
                            if (
                                obj_id in self.targets_needed
                                and obj_id not in self.current_target_hits
                            ):
                                # Hit a valid target!
                                self.current_target_hits.add(obj_id)
                                self.score += 10

                                # Play voice sound for letters
                                if obj.get("type") == "letter" and self.sound_manager:
                                    self.sound_manager.play_voice(obj["value"])

                                # Common destruction effects
                                self.create_explosion(obj["x"], obj["y"])
                                self.create_flame_effect(
                                    self.player_x, self.player_y - 80, obj["x"], obj["y"]
                                )
                                self.center_piece_manager.trigger_convergence(obj["x"], obj["y"])
                                self.apply_explosion_effect(obj["x"], obj["y"], 150, self.letters)

                                # Add visual feedback particles
                                for i in range(20):
                                    self.create_particle(
                                        obj["x"],
                                        obj["y"],
                                        random.choice(FLAME_COLORS),
                                        random.randint(40, 80),
                                        random.uniform(-2, 2),
                                        random.uniform(-2, 2),
                                        20,
                                    )

                                # Remove object and update counts
                                self.letters.remove(obj)
                                self.letters_destroyed += 1

                                # Check if target is complete (letter + both emojis hit)
                                if self.current_target_hits == self.targets_needed:
                                    self._complete_current_target()

                                break  # Exit loop after processing one hit

                    # If no target was hit, add a crack to the screen
                    if not hit_target and self.game_started:
                        self.glass_shatter_manager.handle_misclick(touch_x, touch_y)

            elif event.type == pygame.FINGERUP:
                touch_result = self.multi_touch_manager.handle_touch_up(event)
                if touch_result is not None:
                    touch_id, last_x, last_y = touch_result

        return True

    def _spawn_letters(self):
        """Handle spawning of falling letters and associated emojis."""
        # Spawn letters from the list
        if self.letters_to_spawn:
            if self.frame_count % LETTER_SPAWN_INTERVAL == 0:
                # Use a generic key "value" for letters
                item_value = self.letters_to_spawn.pop(0)

                # Spawn the letter
                letter_obj = {
                    "value": item_value,
                    "x": random.randint(50, self.width - 50),
                    "y": -50,
                    "rect": pygame.Rect(0, 0, 0, 0),  # Will be updated when drawn
                    "size": 240,  # Fixed size (doubled from 120 to 240 for 100% increase)
                    "dx": random.choice([-1, -0.5, 0.5, 1])
                    * 1.5,  # Slightly faster horizontal drift
                    "dy": random.choice([10, 5.5]) * 1.5 * 1.2,  # 20% faster fall speed
                    "can_bounce": False,  # Start without bouncing
                    "mass": random.uniform(140, 160),  # Give items mass for collisions
                    "type": "letter",  # Mark as letter type
                }
                self.letters.append(letter_obj)
                self.letters_spawned += 1

        # Always ensure emojis are available for the current target
        self._ensure_target_emojis_available()

    def _spawn_emojis_for_letter(self, letter):
        """Spawn independent emoji objects for the given letter."""
        emojis = self.resource_manager.get_letter_emojis(letter)

        for i, emoji_surface in enumerate(emojis):
            if emoji_surface is not None:
                # Create independent emoji object
                emoji_obj = {
                    "value": f"{letter}_emoji_{i+1}",
                    "letter": letter,  # Associated letter
                    "emoji_index": i + 1,
                    "x": random.randint(100, self.width - 100),
                    "y": random.randint(-300, -100),  # Spawn higher up
                    "rect": pygame.Rect(0, 0, 0, 0),
                    "size": 96,  # Emoji size
                    "dx": random.choice([-1, -0.5, 0.5, 1]) * 1.2,
                    "dy": random.choice([8, 6]) * 1.2,  # Slightly slower than letters
                    "can_bounce": False,
                    "mass": random.uniform(100, 120),
                    "type": "emoji",
                    "surface": emoji_surface,
                    "hit": False,  # Track if this emoji has been hit
                }
                self.letters.append(emoji_obj)  # Add to same list for physics

    def _ensure_target_emojis_available(self):
        """Ensure emojis are continuously available for the current target letter."""
        if not self.target_letter or not self.targets_needed:
            return

        # Only spawn emojis occasionally to avoid spam (every 60 frames = ~1 second)
        if self.frame_count % 60 != 0:
            return

        # Get current objects on screen
        current_objects = {obj["value"] for obj in self.letters}

        # Ensure the target letter exists on screen (if not hit yet)
        if (
            self.target_letter not in self.current_target_hits
            and self.target_letter not in current_objects
        ):
            # Spawn target letter
            letter_obj = {
                "value": self.target_letter,
                "x": random.randint(50, self.width - 50),
                "y": -50,
                "rect": pygame.Rect(0, 0, 0, 0),
                "size": 240,
                "dx": random.choice([-1, -0.5, 0.5, 1]) * 1.5,
                "dy": random.choice([10, 5.5]) * 1.5 * 1.2,
                "can_bounce": False,
                "mass": random.uniform(140, 160),
                "type": "letter",
            }
            self.letters.append(letter_obj)

        # Ensure both emojis exist on screen (if not hit yet)
        for target_id in self.targets_needed:
            if (
                target_id.startswith(f"{self.target_letter}_emoji_")
                and target_id not in self.current_target_hits
            ):
                if target_id not in current_objects:
                    # Spawn this missing emoji
                    emoji_index = int(target_id.split("_")[-1])  # Get 1 or 2
                    emojis = self.resource_manager.get_letter_emojis(self.target_letter)

                    if emoji_index <= len(emojis):
                        emoji_surface = emojis[emoji_index - 1]  # Convert to 0-based index
                        if emoji_surface is not None:
                            emoji_obj = {
                                "value": target_id,
                                "letter": self.target_letter,
                                "emoji_index": emoji_index,
                                "x": random.randint(100, self.width - 100),
                                "y": random.randint(-300, -100),
                                "rect": pygame.Rect(0, 0, 0, 0),
                                "size": 96,
                                "dx": random.choice([-1, -0.5, 0.5, 1]) * 1.2,
                                "dy": random.choice([8, 6]) * 1.2,
                                "can_bounce": False,
                                "mass": random.uniform(100, 120),
                                "type": "emoji",
                                "surface": emoji_surface,
                                "hit": False,
                            }
                            self.letters.append(emoji_obj)

    def _reset_target_tracking(self, target_letter):
        """Reset tracking for a new target letter."""
        self.current_target_hits.clear()
        self.targets_needed = {
            target_letter,  # The letter itself
            f"{target_letter}_emoji_1",  # First emoji
            f"{target_letter}_emoji_2",  # Second emoji
        }

    def _complete_current_target(self):
        """Handle completion of current target (letter + both emojis hit)."""
        # Move to next target in the group
        if self.target_letter in self.letters_to_target:
            self.letters_to_target.remove(self.target_letter)

        if self.letters_to_target:
            # Move to next letter in current group
            self.target_letter = self.letters_to_target[0]
            # Reset tracking for the new target
            self._reset_target_tracking(self.target_letter)
            # Immediately spawn emojis for the new target
            self._spawn_emojis_for_letter(self.target_letter)
        else:
            # Current group complete - clear current targets
            self.current_target_hits.clear()
            self.targets_needed.clear()

            # Trigger level progression to handle next group setup
            # This will be handled in the main update loop via _handle_level_progression

    def _update_letters(self):
        """Update letter positions and handle collisions."""
        # Update letter positions and bouncing
        for letter_obj in self.letters[:]:
            letter_obj["x"] += letter_obj["dx"]
            letter_obj["y"] += letter_obj["dy"]

            # Bouncing Logic - Allow bouncing only after falling a certain distance
            if not letter_obj["can_bounce"] and letter_obj["y"] > self.height // 5:
                letter_obj["can_bounce"] = True

            # If bouncing is enabled, check screen edges
            if letter_obj["can_bounce"]:
                bounce_dampening = 0.8  # Reduce speed slightly on bounce

                # Left/Right Walls
                if letter_obj["x"] <= 0 + letter_obj.get("size", 50) / 2:  # Approx radius check
                    letter_obj["x"] = 0 + letter_obj.get("size", 50) / 2
                    letter_obj["dx"] = abs(letter_obj["dx"]) * bounce_dampening
                elif letter_obj["x"] >= self.width - letter_obj.get("size", 50) / 2:
                    letter_obj["x"] = self.width - letter_obj.get("size", 50) / 2
                    letter_obj["dx"] = -abs(letter_obj["dx"]) * bounce_dampening

                # Top/Bottom Walls (less likely to hit top unless pushed)
                if letter_obj["y"] <= 0 + letter_obj.get("size", 50) / 2:
                    letter_obj["y"] = 0 + letter_obj.get("size", 50) / 2
                    letter_obj["dy"] = abs(letter_obj["dy"]) * bounce_dampening
                elif letter_obj["y"] >= self.height - letter_obj.get("size", 50) / 2:
                    letter_obj["y"] = self.height - letter_obj.get("size", 50) / 2
                    letter_obj["dy"] = -abs(letter_obj["dy"]) * bounce_dampening
                    # Also slightly push horizontally away from edge on bottom bounce
                    letter_obj["dx"] *= bounce_dampening
                    if letter_obj["x"] < self.width / 2:
                        letter_obj["dx"] += random.uniform(0.1, 0.3)
                    else:
                        letter_obj["dx"] -= random.uniform(0.1, 0.3)

        # Simple Collision Detection Between Items
        # Reduce collision check frequency for performance
        collision_frequency = 2  # Check every 2 frames for performance
        if self.frame_count % collision_frequency == 0:
            for i, letter_obj1 in enumerate(self.letters):
                for j in range(i + 1, len(self.letters)):
                    letter_obj2 = self.letters[j]
                    dx = letter_obj2["x"] - letter_obj1["x"]
                    dy = letter_obj2["y"] - letter_obj1["y"]
                    distance_sq = dx * dx + dy * dy  # Use squared distance for efficiency

                    # Approximate collision radius based on font/shape size
                    # Use a slightly larger radius for text to account for varying widths
                    radius1 = (
                        letter_obj1.get("size", self.target_font.get_height()) / 1.8
                    )  # Approx radius
                    radius2 = letter_obj2.get("size", self.target_font.get_height()) / 1.8
                    min_distance = radius1 + radius2
                    min_distance_sq = min_distance * min_distance

                    if distance_sq < min_distance_sq and distance_sq > 0:  # Check for overlap
                        distance = math.sqrt(distance_sq)
                        # Normalize collision vector
                        nx = dx / distance
                        ny = dy / distance

                        # Resolve interpenetration (push apart)
                        overlap = min_distance - distance
                        total_mass = letter_obj1["mass"] + letter_obj2["mass"]
                        # Push apart proportional to the *other* object's mass
                        push_factor = overlap / total_mass
                        letter_obj1["x"] -= nx * push_factor * letter_obj2["mass"]
                        letter_obj1["y"] -= ny * push_factor * letter_obj2["mass"]
                        letter_obj2["x"] += nx * push_factor * letter_obj1["mass"]
                        letter_obj2["y"] += ny * push_factor * letter_obj1["mass"]

                        # Calculate collision response (bounce) - Elastic collision formula component
                        # Relative velocity
                        dvx = letter_obj1["dx"] - letter_obj2["dx"]
                        dvy = letter_obj1["dy"] - letter_obj2["dy"]
                        # Dot product of relative velocity and collision normal
                        dot_product = dvx * nx + dvy * ny
                        # Impulse magnitude
                        impulse = (2 * dot_product) / total_mass
                        bounce_factor = 0.85  # Slightly less than perfectly elastic

                        # Apply impulse scaled by mass and bounce factor
                        letter_obj1["dx"] -= impulse * letter_obj2["mass"] * nx * bounce_factor
                        letter_obj1["dy"] -= impulse * letter_obj2["mass"] * ny * bounce_factor
                        letter_obj2["dx"] += impulse * letter_obj1["mass"] * nx * bounce_factor
                        letter_obj2["dy"] += impulse * letter_obj1["mass"] * ny * bounce_factor

    def _handle_checkpoint_logic(self):
        """Handle checkpoint screen display logic."""
        # Update overall destroyed count
        self.overall_destroyed = self.total_destroyed + self.letters_destroyed

        # Handle checkpoint waiting state
        if self.checkpoint_waiting:
            if self.checkpoint_delay_frames <= 0:
                self.checkpoint_waiting = False
                if not self.checkpoint_manager.show_checkpoint_screen(
                    self.screen, "alphabet"
                ):  # If checkpoint returns False (chose Menu)
                    self.running = False  # Exit game loop to return to menu
                else:
                    # If continue was pressed
                    self.game_started = True  # Resume the current level
            else:
                self.checkpoint_delay_frames -= 1

        # Check if we hit a new checkpoint threshold (and not just completed a level)
        elif (
            self.overall_destroyed > 0
            and self.overall_destroyed % 10 == 0
            and self.overall_destroyed // 10 > self.last_checkpoint_triggered
            and not self.just_completed_level
        ):
            self.last_checkpoint_triggered = self.overall_destroyed // 10
            self.checkpoint_waiting = True
            self.checkpoint_delay_frames = 60  # Wait ~1 second (60 frames) for animations

    def _handle_level_progression(self):
        """Handle level progression and completion logic."""
        # Check if the current group is finished (no letters left on screen AND no more to spawn)
        if (
            not self.letters and not self.letters_to_spawn and self.letters_to_target == []
        ):  # Ensure targets are also cleared
            self.total_destroyed += self.letters_destroyed  # Add destroyed from this group to total
            self.current_group_index += 1
            self.just_completed_level = True  # Set flag to prevent immediate checkpoint

            if self.current_group_index < len(self.groups):
                # Start Next Group
                self.current_group = self.groups[self.current_group_index]
                self.letters_to_spawn = self.current_group.copy()
                self.letters_to_target = self.current_group.copy()
                if self.letters_to_target:
                    self.target_letter = self.letters_to_target[0]
                    # Set up target tracking for the new letter
                    self._reset_target_tracking(self.target_letter)
                    # Immediately spawn emojis for the new target
                    self._spawn_emojis_for_letter(self.target_letter)
                else:
                    print(f"Warning: Group {self.current_group_index} is empty.")
                    # Handle this case - maybe skip group or end game?
                    self.running = False  # End game for now if a group is empty
                    return False

                # Reset group-specific counters
                self.letters_destroyed = 0
                self.letters_spawned = 0
                self.just_completed_level = False  # Reset flag for the new level
                self.game_started = True  # Ensure game continues if paused by checkpoint logic bug
                self.last_checkpoint_triggered = (
                    self.overall_destroyed // 10
                )  # Update checkpoint trigger base

            else:
                # All Groups Completed (Level Finished)
                # Show checkpoint screen for all completed levels
                pygame.time.delay(500)  # Brief delay like in colors level
                if not self.checkpoint_manager.show_checkpoint_screen(
                    self.screen, "alphabet"
                ):  # If checkpoint returns False (chose Menu)
                    self.running = False  # Exit game loop to return to menu
                    return False
                else:
                    # If continue was pressed, return to menu since level is complete
                    self.running = False
                    return False

        return None  # Continue the level

    def _draw_frame(self, stars):
        """Draw a single frame of the alphabet level."""
        # Update glass shatter manager
        self.glass_shatter_manager.update()

        # Apply screen shake if active
        offset_x, offset_y = self.glass_shatter_manager.get_screen_shake_offset()

        # Fill background based on shatter state
        self.screen.fill(self.glass_shatter_manager.get_background_color())

        # Draw cracks
        self.glass_shatter_manager.draw_cracks(self.screen)

        # Draw Background Elements (Stars)
        for star in stars:
            x, y, radius = star
            y += 1  # Slower star movement speed
            pygame.draw.circle(self.screen, (200, 200, 200), (x + offset_x, y + offset_y), radius)
            if y > self.height + radius:  # Reset when fully off screen
                y = random.randint(-50, -10)
                x = random.randint(0, self.width)
            star[1] = y
            star[0] = x

        # Draw Center Piece (Swirl Particles + Target Display)
        self.center_piece_manager.update_and_draw(
            self.screen, self.target_letter, "alphabet", offset_x, offset_y
        )

        # Update and Draw Falling Objects (Letters and Emojis)
        for obj in self.letters[:]:
            draw_pos_x = int(obj["x"] + offset_x)
            draw_pos_y = int(obj["y"] + offset_y)

            if obj.get("type") == "letter":
                # Draw Letter
                display_value = obj["value"]

                # Greek alpha special case for alphabet mode
                if obj["value"] == "a":
                    display_value = "α"

                # Highlight if this is part of current target
                is_target = obj["value"] in self.targets_needed
                text_color = BLACK if is_target else (150, 150, 150)

                # PERFORMANCE OPTIMIZATION: Use cached font surface if available
                try:
                    cached_surface = self.resource_manager.get_falling_object_surface(
                        "alphabet", obj["value"], text_color
                    )
                    text_rect = cached_surface.get_rect(center=(draw_pos_x, draw_pos_y))
                    # Inflate rect by 50% for easier interaction (25 pixels on each side)
                    interaction_rect = text_rect.inflate(50, 50)
                    obj["rect"] = interaction_rect
                    self.screen.blit(cached_surface, text_rect)
                except:
                    # Fallback: Original rendering method
                    text_surface = self.target_font.render(display_value, True, text_color)
                    text_rect = text_surface.get_rect(center=(draw_pos_x, draw_pos_y))
                    # Inflate rect by 50% for easier interaction (25 pixels on each side)
                    interaction_rect = text_rect.inflate(50, 50)
                    obj["rect"] = interaction_rect
                    self.screen.blit(text_surface, text_rect)

            elif obj.get("type") == "emoji":
                # Draw Emoji
                emoji_surface = obj.get("surface")
                if emoji_surface:
                    # Highlight if this is part of current target
                    is_target = obj["value"] in self.targets_needed

                    if is_target:
                        # Full opacity for target emojis
                        emoji_rect = emoji_surface.get_rect(center=(draw_pos_x, draw_pos_y))
                        self.screen.blit(emoji_surface, emoji_rect)
                    else:
                        # Reduced opacity for non-target emojis
                        emoji_copy = emoji_surface.copy()
                        emoji_copy.set_alpha(128)  # 50% transparency
                        emoji_rect = emoji_copy.get_rect(center=(draw_pos_x, draw_pos_y))
                        self.screen.blit(emoji_copy, emoji_rect)

                    # Set collision rect (larger for easier clicking)
                    obj["rect"] = emoji_rect.inflate(20, 20)

        # Process Flamethrower Effects
        self.flamethrower_manager.update()
        self.flamethrower_manager.draw(self.screen, offset_x, offset_y)

        # Process Legacy Lasers (if any remain)
        for laser in self.lasers[:]:
            if laser["duration"] > 0:
                # Legacy laser handling (non-flamethrower effects)
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

        # Process Explosions
        for explosion in self.explosions[:]:
            if explosion["duration"] > 0:
                self.draw_explosion(explosion, offset_x, offset_y)  # Pass shake offset
                explosion["duration"] -= 1
            else:
                self.explosions.remove(explosion)

        # Display HUD
        self.hud_manager.display_info(
            self.screen,
            self.score,
            self.current_ability,
            self.target_letter,
            self.overall_destroyed + self.letters_destroyed,
            self.TOTAL_LETTERS,
            "alphabet",
        )

    # Implement abstract methods from BaseLevel
    def get_mode_name(self) -> str:
        """Return the mode name for this level."""
        return "alphabet"

    def get_groups(self) -> List[List]:
        """Return the groups for this level."""
        return self.groups

    def get_total_objects(self) -> int:
        """Return the total number of objects in this level."""
        return self.TOTAL_LETTERS

    def _setup_target_tracking(self):
        """Setup target tracking for the current target."""
        if self.target_letter:
            self._reset_target_tracking(self.target_letter)

    def _should_destroy_object(self, obj) -> bool:
        """Override to define hit conditions for alphabet level."""
        # For alphabet level, objects are destroyed if they're part of current target
        obj_id = obj.value if hasattr(obj, 'value') else str(obj)
        return obj_id in self.targets_needed and obj_id not in self.current_target_hits

    def _create_game_object(self, obj_data: Dict[str, Any]):
        """Create a game object from data for alphabet level."""
        value = obj_data.get("value", "")
        x = obj_data.get("x", random.randint(50, self.width - 50))
        y = obj_data.get("y", -50)

        # Create letter object using factory
        return self.object_factory.create_letter_object(value, x, y)

    def _draw_game_objects(self, offset_x: float, offset_y: float):
        """Draw alphabet-specific game objects."""
        for obj in self.letters[:]:
            draw_pos_x = int(obj["x"] + offset_x)
            draw_pos_y = int(obj["y"] + offset_y)

            if obj.get("type") == "letter":
                # Draw Letter
                display_value = obj["value"]
                if obj["value"] == "a":
                    display_value = "α"

                is_target = obj["value"] in self.targets_needed
                text_color = BLACK if is_target else (150, 150, 150)

                try:
                    cached_surface = self.resource_manager.get_falling_object_surface(
                        "alphabet", obj["value"], text_color
                    )
                    text_rect = cached_surface.get_rect(center=(draw_pos_x, draw_pos_y))
                    interaction_rect = text_rect.inflate(50, 50)
                    obj["rect"] = interaction_rect
                    self.screen.blit(cached_surface, text_rect)
                except:
                    text_surface = self.target_font.render(display_value, True, text_color)
                    text_rect = text_surface.get_rect(center=(draw_pos_x, draw_pos_y))
                    interaction_rect = text_rect.inflate(50, 50)
                    obj["rect"] = interaction_rect
                    self.screen.blit(text_surface, text_rect)

            elif obj.get("type") == "emoji":
                emoji_surface = obj.get("surface")
                if emoji_surface:
                    is_target = obj["value"] in self.targets_needed
                    if is_target:
                        emoji_rect = emoji_surface.get_rect(center=(draw_pos_x, draw_pos_y))
                        self.screen.blit(emoji_surface, emoji_rect)
                    else:
                        emoji_copy = emoji_surface.copy()
                        emoji_copy.set_alpha(128)
                        emoji_rect = emoji_copy.get_rect(center=(draw_pos_x, draw_pos_y))
                        self.screen.blit(emoji_copy, emoji_rect)

                    obj["rect"] = emoji_rect.inflate(20, 20)
