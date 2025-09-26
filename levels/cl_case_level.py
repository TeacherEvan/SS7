import math
import random

import pygame

from settings import (
    BLACK,
    FLAME_COLORS,
    GROUP_SIZE,
    LETTER_SPAWN_INTERVAL,
    LEVEL_PROGRESS_PATH,
    SEQUENCES,
    WHITE,
)
from universal_class import (
    CenterPieceManager,
    CheckpointManager,
    FlamethrowerManager,
    GlassShatterManager,
    HUDManager,
    MultiTouchManager,
)


class CLCaseLevel:
    """
    Handles the C/L Case level gameplay logic.
    Sequential letter targeting through lowercase alphabet a-z.
    Special feature: 'a' is displayed as 'α' (Greek alpha).
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
        Initialize the C/L Case level.

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
        """
        self.width = width
        self.height = height
        self.screen = screen
        self.fonts = fonts
        self.small_font = small_font
        self.target_font = target_font
        self.particle_manager = particle_manager
        self.glass_shatter_manager = glass_shatter_manager
        self.multi_touch_manager = multi_touch_manager
        self.hud_manager = hud_manager
        self.checkpoint_manager = checkpoint_manager
        self.center_piece_manager = center_piece_manager
        self.flamethrower_manager = flamethrower_manager
        self.resource_manager = resource_manager
        self.create_explosion = create_explosion_func
        self.create_flame_effect = create_flame_effect_func
        self.apply_explosion_effect = apply_explosion_effect_func
        self.create_particle = create_particle_func
        self.explosions = explosions_list
        self.lasers = lasers_list
        self.draw_explosion = draw_explosion_func
        self.game_over_screen = game_over_screen_func
        self.sound_manager = sound_manager

        # C/L Case configuration
        self.sequence = SEQUENCES["clcase"]
        self.groups = [
            self.sequence[i : i + GROUP_SIZE] for i in range(0, len(self.sequence), GROUP_SIZE)
        ]
        self.TOTAL_LETTERS = len(self.sequence)

        # Game state variables
        self.reset_level_state()

        # Emoji system for visual learning
        self.emoji_objects = []  # Independent emoji targets
        self.targets_needed = (
            {}
        )  # Track what targets are needed: {'letter': count, 'emoji1': count, 'emoji2': count}

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

        # Checkpoint flags
        self.checkpoint_waiting = False
        self.checkpoint_delay_frames = 0
        self.just_completed_level = False

        # Game state
        self.letters = []  # items on screen
        self.letters_to_spawn = self.current_group.copy()
        self.emoji_objects = []  # emoji targets on screen
        self.targets_needed = {}  # Track what targets are needed for completion
        self.frame_count = 0

        # Initialize target tracking for the current group
        self._reset_target_tracking()
        self.game_started = False
        self.last_click_time = 0
        self.player_x = self.width // 2
        self.player_y = self.height // 2
        self.player_color_index = 0
        self.click_cooldown = 0
        self.mouse_down = False
        self.mouse_press_time = 0
        self.click_count = 0

        # Abilities
        self.abilities = ["laser", "aoe", "charge_up"]
        self.current_ability = "laser"

        # Effects management
        self.glass_shatter_manager.reset()
        self.multi_touch_manager.reset()
        self.flamethrower_manager.clear()
        self.center_piece_manager.reset()

    def _reset_target_tracking(self):
        """Reset target tracking for the current target letter."""
        if self.target_letter:
            # Each target letter needs: the letter itself + 2 emojis
            self.targets_needed = {
                self.target_letter: 1,
                f"{self.target_letter}_emoji1": 1,
                f"{self.target_letter}_emoji2": 1,
            }
        else:
            self.targets_needed = {}

    def _complete_current_target(self):
        """Complete the current target and move to next letter."""
        if self.target_letter in self.letters_to_target:
            self.letters_to_target.remove(self.target_letter)

        if self.letters_to_target:
            self.target_letter = self.letters_to_target[0]
            self._reset_target_tracking()
        else:
            # Group is complete
            self.targets_needed = {}
            self.target_letter = None

    def _is_current_target_complete(self):
        """Check if all required targets for current letter are hit."""
        if not self.targets_needed:
            return True
        return all(count == 0 for count in self.targets_needed.values())

    def _ensure_target_emojis_available(self):
        """Ensure emoji targets are available on screen when needed."""
        if not self.target_letter or not self.resource_manager.has_emojis_for_letter(
            self.target_letter
        ):
            return

        # Only spawn emojis every 60 frames (about 1.2 seconds at 50 FPS) to avoid overwhelming
        if self.frame_count % 60 != 0:
            return

        # Check what emoji targets are missing from screen
        emoji_types_on_screen = set()
        for emoji_obj in self.emoji_objects:
            if emoji_obj["letter"] == self.target_letter:
                emoji_types_on_screen.add(emoji_obj["emoji_type"])

        # Spawn missing emoji targets
        for emoji_type in ["emoji1", "emoji2"]:
            target_key = f"{self.target_letter}_{emoji_type}"
            if (
                self.targets_needed.get(target_key, 0) > 0
                and emoji_type not in emoji_types_on_screen
            ):
                self._spawn_emoji_target(self.target_letter, emoji_type)

    def _spawn_emoji_target(self, letter, emoji_type):
        """Spawn an emoji target for the given letter and type."""
        emojis = self.resource_manager.get_letter_emojis(letter)
        if not emojis:
            return

        emoji_index = 0 if emoji_type == "emoji1" else 1
        if emoji_index >= len(emojis):
            return

        emoji_surface = emojis[emoji_index]
        emoji_obj = {
            "letter": letter,
            "emoji_type": emoji_type,
            "surface": emoji_surface,
            "x": random.randint(50, self.width - 50),
            "y": -50,
            "rect": pygame.Rect(0, 0, 0, 0),  # Will be updated when drawn
            "dx": random.choice([-1, -0.5, 0.5, 1]) * 1.5,
            "dy": random.choice([5, 10.5]) * 1.5 * 1.2,  # Same speed as letters
            "can_bounce": False,
            "mass": random.uniform(40, 60),
        }
        self.emoji_objects.append(emoji_obj)

    def _update_emojis(self):
        """Update emoji positions and physics."""
        for emoji_obj in self.emoji_objects[:]:
            emoji_obj["x"] += emoji_obj["dx"]
            emoji_obj["y"] += emoji_obj["dy"]

            # Bouncing logic (same as letters)
            if not emoji_obj["can_bounce"] and emoji_obj["y"] > self.height // 5:
                emoji_obj["can_bounce"] = True

            if emoji_obj["can_bounce"]:
                bounce_dampening = 0.8

                # Get emoji size for bounds checking
                emoji_size = emoji_obj["surface"].get_width()

                # Left/Right Walls
                if emoji_obj["x"] <= 0 + emoji_size / 2:
                    emoji_obj["x"] = 0 + emoji_size / 2
                    emoji_obj["dx"] = abs(emoji_obj["dx"]) * bounce_dampening
                elif emoji_obj["x"] >= self.width - emoji_size / 2:
                    emoji_obj["x"] = self.width - emoji_size / 2
                    emoji_obj["dx"] = -abs(emoji_obj["dx"]) * bounce_dampening

                # Top/Bottom Walls
                if emoji_obj["y"] <= 0 + emoji_size / 2:
                    emoji_obj["y"] = 0 + emoji_size / 2
                    emoji_obj["dy"] = abs(emoji_obj["dy"]) * bounce_dampening
                elif emoji_obj["y"] >= self.height - emoji_size / 2:
                    emoji_obj["y"] = self.height - emoji_size / 2
                    emoji_obj["dy"] = -abs(emoji_obj["dy"]) * bounce_dampening
                    emoji_obj["dx"] *= bounce_dampening
                    if emoji_obj["x"] < self.width / 2:
                        emoji_obj["dx"] += random.uniform(0.1, 0.3)
                    else:
                        emoji_obj["dx"] -= random.uniform(0.1, 0.3)

    def run(self):
        """
        Main entry point for the C/L Case level.

        Returns:
            bool: True if should return to menu, False if exiting completely
        """
        print("Starting C/L Case level...")

        # Initialize background stars
        stars = []
        for _ in range(100):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            radius = random.randint(2, 4)
            stars.append([x, y, radius])

        # Main game loop
        running = True
        clock = pygame.time.Clock()

        while running:
            # Handle events
            for event in pygame.event.get():
                if self._handle_events(event):
                    running = False
                    break

            if not running:
                break

            # Spawn letters and emojis
            if self.game_started:
                self._spawn_letters()
                self._ensure_target_emojis_available()

            # Update letters, emojis and collisions
            self._update_letters()
            self._update_emojis()

            # Draw frame
            self._draw_frame(stars)

            # Handle checkpoint logic
            if self._handle_checkpoint_logic():
                running = False
                break

            # Handle level progression
            progression_result = self._handle_level_progression()
            if progression_result is not None:
                return progression_result

            # Update display
            pygame.display.flip()
            clock.tick(50)  # 50 FPS for performance
            self.frame_count += 1

        return True  # Return to menu by default

    def _handle_events(self, event):
        """
        Handle pygame events for the C/L Case level.

        Args:
            event: pygame event object

        Returns:
            bool: True if should exit, False otherwise
        """
        # Handle glass shatter events first
        self.glass_shatter_manager.handle_event(event)

        if event.type == pygame.QUIT:
            return True

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Return to level menu instead of exiting the game completely
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

        elif event.type == pygame.FINGERDOWN:
            touch_result = self.multi_touch_manager.handle_touch_down(event)
            if touch_result is None:
                return False  # Touch was ignored due to cooldown
            touch_id, touch_x, touch_y = touch_result
            if not self.game_started:
                self.game_started = True
            else:
                self._handle_click(touch_x, touch_y)

        elif event.type == pygame.FINGERUP:
            touch_result = self.multi_touch_manager.handle_touch_up(event)

        return False

    def _handle_click(self, click_x, click_y):
        """
        Handle click/touch on the screen.

        Args:
            click_x (float): X coordinate of click
            click_y (float): Y coordinate of click
        """
        current_time = pygame.time.get_ticks()
        self.last_click_time = current_time

        # Flag to track if click hit a target
        hit_target = False

        # Process click on letter targets
        for letter_obj in self.letters[:]:
            if letter_obj["rect"].collidepoint(click_x, click_y):
                hit_target = True
                if letter_obj["value"] == self.target_letter:
                    self.score += 10
                    # Play voice sound for destroyed target
                    if self.sound_manager:
                        self.sound_manager.play_voice(letter_obj["value"])
                    # Common destruction effects
                    self.create_explosion(letter_obj["x"], letter_obj["y"])
                    self.create_flame_effect(
                        self.player_x, self.player_y - 80, letter_obj["x"], letter_obj["y"]
                    )
                    self.center_piece_manager.trigger_convergence(letter_obj["x"], letter_obj["y"])
                    self.apply_explosion_effect(letter_obj["x"], letter_obj["y"], 150, self.letters)

                    # Add visual feedback particles
                    for i in range(20):
                        self.create_particle(
                            letter_obj["x"],
                            letter_obj["y"],
                            random.choice(FLAME_COLORS),
                            random.randint(40, 80),
                            random.uniform(-2, 2),
                            random.uniform(-2, 2),
                            20,
                        )

                    # Remove letter and update target tracking
                    self.letters.remove(letter_obj)
                    self.letters_destroyed += 1

                    # Mark letter target as completed
                    if self.target_letter in self.targets_needed:
                        self.targets_needed[self.target_letter] = 0

                    # Check if current target is complete
                    if self._is_current_target_complete():
                        self._complete_current_target()
                    break
                else:
                    # Add feedback for clicking wrong target - shake removed
                    pass

        # Process click on emoji targets
        if not hit_target:
            for emoji_obj in self.emoji_objects[:]:
                if emoji_obj["rect"].collidepoint(click_x, click_y):
                    # Check if this emoji belongs to the current target letter
                    if emoji_obj["letter"] == self.target_letter:
                        hit_target = True
                        self.score += 5  # Emojis worth 5 points

                        # Play voice sound for the letter this emoji represents
                        if self.sound_manager:
                            self.sound_manager.play_voice(emoji_obj["letter"])

                        # Common destruction effects
                        self.create_explosion(emoji_obj["x"], emoji_obj["y"])
                        self.create_flame_effect(
                            self.player_x, self.player_y - 80, emoji_obj["x"], emoji_obj["y"]
                        )
                        self.center_piece_manager.trigger_convergence(
                            emoji_obj["x"], emoji_obj["y"]
                        )
                        self.apply_explosion_effect(
                            emoji_obj["x"], emoji_obj["y"], 150, self.emoji_objects
                        )

                        # Add visual feedback particles
                        for i in range(15):
                            self.create_particle(
                                emoji_obj["x"],
                                emoji_obj["y"],
                                random.choice(FLAME_COLORS),
                                random.randint(30, 60),
                                random.uniform(-1.5, 1.5),
                                random.uniform(-1.5, 1.5),
                                15,
                            )

                        # Remove emoji and update target tracking
                        self.emoji_objects.remove(emoji_obj)

                        # Mark emoji target as completed
                        target_key = f"{emoji_obj['letter']}_{emoji_obj['emoji_type']}"
                        if target_key in self.targets_needed:
                            self.targets_needed[target_key] = 0

                        # Check if current target is complete
                        if self._is_current_target_complete():
                            self._complete_current_target()
                        break

        # If no target was hit, add a crack to the screen
        if not hit_target and self.game_started:
            self.glass_shatter_manager.handle_misclick(click_x, click_y)

    def _spawn_letters(self):
        """Spawn letters at regular intervals."""
        if self.letters_to_spawn:
            if self.frame_count % LETTER_SPAWN_INTERVAL == 0:
                item_value = self.letters_to_spawn.pop(0)
                letter_obj = {
                    "value": item_value,
                    "x": random.randint(50, self.width - 50),
                    "y": -50,
                    "rect": pygame.Rect(0, 0, 0, 0),  # Will be updated when drawn
                    "size": 240,  # Fixed size
                    "dx": random.choice([-1, -0.5, 0.5, 1]) * 1.5,
                    "dy": random.choice([5, 10.5]) * 1.5 * 1.2,  # 20% faster fall speed
                    "can_bounce": False,  # Start without bouncing
                    "mass": random.uniform(40, 60),  # Give items mass for collisions 40/60
                }
                self.letters.append(letter_obj)
                self.letters_spawned += 1

    def _update_letters(self):
        """Update letter positions, bouncing, and collisions."""
        # Update letter positions
        for letter_obj in self.letters[:]:
            letter_obj["x"] += letter_obj["dx"]
            letter_obj["y"] += letter_obj["dy"]

            # Bouncing logic
            if not letter_obj["can_bounce"] and letter_obj["y"] > self.height // 5:
                letter_obj["can_bounce"] = True

            if letter_obj["can_bounce"]:
                bounce_dampening = 0.8

                # Left/Right Walls
                if letter_obj["x"] <= 0 + letter_obj.get("size", 50) / 2:
                    letter_obj["x"] = 0 + letter_obj.get("size", 50) / 2
                    letter_obj["dx"] = abs(letter_obj["dx"]) * bounce_dampening
                elif letter_obj["x"] >= self.width - letter_obj.get("size", 50) / 2:
                    letter_obj["x"] = self.width - letter_obj.get("size", 50) / 2
                    letter_obj["dx"] = -abs(letter_obj["dx"]) * bounce_dampening

                # Top/Bottom Walls
                if letter_obj["y"] <= 0 + letter_obj.get("size", 50) / 2:
                    letter_obj["y"] = 0 + letter_obj.get("size", 50) / 2
                    letter_obj["dy"] = abs(letter_obj["dy"]) * bounce_dampening
                elif letter_obj["y"] >= self.height - letter_obj.get("size", 50) / 2:
                    letter_obj["y"] = self.height - letter_obj.get("size", 50) / 2
                    letter_obj["dy"] = -abs(letter_obj["dy"]) * bounce_dampening
                    letter_obj["dx"] *= bounce_dampening
                    if letter_obj["x"] < self.width / 2:
                        letter_obj["dx"] += random.uniform(0.1, 0.3)
                    else:
                        letter_obj["dx"] -= random.uniform(0.1, 0.3)

        # Handle collisions
        self._handle_letter_collisions()
        self._handle_emoji_collisions()
        self._handle_letter_emoji_collisions()

    def _handle_letter_collisions(self):
        """Handle collisions between letters with physics."""
        collision_frequency = 3  # Check every 3 frames for performance
        if self.frame_count % collision_frequency == 0:
            for i, letter_obj1 in enumerate(self.letters):
                for j in range(i + 1, len(self.letters)):
                    letter_obj2 = self.letters[j]
                    dx = letter_obj2["x"] - letter_obj1["x"]
                    dy = letter_obj2["y"] - letter_obj1["y"]
                    distance_sq = dx * dx + dy * dy

                    # Collision radius calculation
                    radius1 = letter_obj1.get("size", self.target_font.get_height()) / 1.8
                    radius2 = letter_obj2.get("size", self.target_font.get_height()) / 1.8
                    min_distance = radius1 + radius2
                    min_distance_sq = min_distance * min_distance

                    if distance_sq < min_distance_sq and distance_sq > 0:
                        distance = math.sqrt(distance_sq)
                        # Normalize collision vector
                        nx = dx / distance
                        ny = dy / distance

                        # Resolve interpenetration
                        overlap = min_distance - distance
                        total_mass = letter_obj1["mass"] + letter_obj2["mass"]
                        push_factor = overlap / total_mass
                        letter_obj1["x"] -= nx * push_factor * letter_obj2["mass"]
                        letter_obj1["y"] -= ny * push_factor * letter_obj2["mass"]
                        letter_obj2["x"] += nx * push_factor * letter_obj1["mass"]
                        letter_obj2["y"] += ny * push_factor * letter_obj1["mass"]

                        # Calculate collision response
                        dvx = letter_obj1["dx"] - letter_obj2["dx"]
                        dvy = letter_obj1["dy"] - letter_obj2["dy"]
                        dot_product = dvx * nx + dvy * ny
                        impulse = (2 * dot_product) / total_mass
                        bounce_factor = 0.85

                        letter_obj1["dx"] -= impulse * letter_obj2["mass"] * nx * bounce_factor
                        letter_obj1["dy"] -= impulse * letter_obj2["mass"] * ny * bounce_factor
                        letter_obj2["dx"] += impulse * letter_obj1["mass"] * nx * bounce_factor
                        letter_obj2["dy"] += impulse * letter_obj1["mass"] * ny * bounce_factor

    def _handle_emoji_collisions(self):
        """Handle collisions between emoji objects."""
        collision_frequency = 3  # Check every 3 frames for performance
        if self.frame_count % collision_frequency == 0:
            for i, emoji1 in enumerate(self.emoji_objects):
                for j in range(i + 1, len(self.emoji_objects)):
                    emoji2 = self.emoji_objects[j]
                    dx = emoji2["x"] - emoji1["x"]
                    dy = emoji2["y"] - emoji1["y"]
                    distance_sq = dx * dx + dy * dy

                    # Collision radius calculation
                    radius1 = emoji1["surface"].get_width() / 2
                    radius2 = emoji2["surface"].get_width() / 2
                    min_distance = radius1 + radius2
                    min_distance_sq = min_distance * min_distance

                    if distance_sq < min_distance_sq and distance_sq > 0:
                        distance = math.sqrt(distance_sq)
                        # Normalize collision vector
                        nx = dx / distance
                        ny = dy / distance

                        # Resolve interpenetration
                        overlap = min_distance - distance
                        total_mass = emoji1["mass"] + emoji2["mass"]
                        push_factor = overlap / total_mass
                        emoji1["x"] -= nx * push_factor * emoji2["mass"]
                        emoji1["y"] -= ny * push_factor * emoji2["mass"]
                        emoji2["x"] += nx * push_factor * emoji1["mass"]
                        emoji2["y"] += ny * push_factor * emoji1["mass"]

                        # Calculate collision response
                        dvx = emoji1["dx"] - emoji2["dx"]
                        dvy = emoji1["dy"] - emoji2["dy"]
                        dot_product = dvx * nx + dvy * ny
                        impulse = (2 * dot_product) / total_mass
                        bounce_factor = 0.85

                        emoji1["dx"] -= impulse * emoji2["mass"] * nx * bounce_factor
                        emoji1["dy"] -= impulse * emoji2["mass"] * ny * bounce_factor
                        emoji2["dx"] += impulse * emoji1["mass"] * nx * bounce_factor
                        emoji2["dy"] += impulse * emoji1["mass"] * ny * bounce_factor

    def _handle_letter_emoji_collisions(self):
        """Handle collisions between letters and emojis."""
        collision_frequency = 3  # Check every 3 frames for performance
        if self.frame_count % collision_frequency == 0:
            for letter_obj in self.letters:
                for emoji_obj in self.emoji_objects:
                    dx = emoji_obj["x"] - letter_obj["x"]
                    dy = emoji_obj["y"] - letter_obj["y"]
                    distance_sq = dx * dx + dy * dy

                    # Collision radius calculation
                    letter_radius = letter_obj.get("size", self.target_font.get_height()) / 1.8
                    emoji_radius = emoji_obj["surface"].get_width() / 2
                    min_distance = letter_radius + emoji_radius
                    min_distance_sq = min_distance * min_distance

                    if distance_sq < min_distance_sq and distance_sq > 0:
                        distance = math.sqrt(distance_sq)
                        # Normalize collision vector
                        nx = dx / distance
                        ny = dy / distance

                        # Resolve interpenetration
                        overlap = min_distance - distance
                        total_mass = letter_obj["mass"] + emoji_obj["mass"]
                        push_factor = overlap / total_mass
                        letter_obj["x"] -= nx * push_factor * emoji_obj["mass"]
                        letter_obj["y"] -= ny * push_factor * emoji_obj["mass"]
                        emoji_obj["x"] += nx * push_factor * letter_obj["mass"]
                        emoji_obj["y"] += ny * push_factor * letter_obj["mass"]

                        # Calculate collision response
                        dvx = letter_obj["dx"] - emoji_obj["dx"]
                        dvy = letter_obj["dy"] - emoji_obj["dy"]
                        dot_product = dvx * nx + dvy * ny
                        impulse = (2 * dot_product) / total_mass
                        bounce_factor = 0.85

                        letter_obj["dx"] -= impulse * emoji_obj["mass"] * nx * bounce_factor
                        letter_obj["dy"] -= impulse * emoji_obj["mass"] * ny * bounce_factor
                        emoji_obj["dx"] += impulse * letter_obj["mass"] * nx * bounce_factor
                        emoji_obj["dy"] += impulse * letter_obj["mass"] * ny * bounce_factor

    def _handle_checkpoint_logic(self):
        """
        Handle checkpoint display logic.

        Returns:
            bool: True if should exit to menu, False otherwise
        """
        self.overall_destroyed = self.total_destroyed + self.letters_destroyed

        # If waiting for animations before showing checkpoint screen
        if self.checkpoint_waiting:
            if (
                self.checkpoint_delay_frames <= 0
                and len(self.explosions) <= 1
                and len(self.lasers) <= 1
                and self.flamethrower_manager.get_count() <= 1
            ):

                self.checkpoint_waiting = False
                self.game_started = False  # Pause the game
                if not self.checkpoint_manager.show_checkpoint_screen(self.screen, "clcase"):
                    return True  # Exit to menu
                else:
                    self.game_started = True  # Resume the current level
            else:
                self.checkpoint_delay_frames -= 1

        # Check if we hit a new checkpoint threshold
        elif (
            self.overall_destroyed > 0
            and self.overall_destroyed % 10 == 0
            and self.overall_destroyed // 10 > self.last_checkpoint_triggered
            and not self.just_completed_level
        ):

            self.last_checkpoint_triggered = self.overall_destroyed // 10
            self.checkpoint_waiting = True
            self.checkpoint_delay_frames = 60  # Wait ~1 second for animations

        return False

    def _handle_level_progression(self):
        """
        Handle progression through letter groups and level completion.

        Returns:
            None if level continues, bool if level should exit
        """
        # Check if the current group is finished (no more letters, emojis, or targets)
        if (
            not self.letters
            and not self.letters_to_spawn
            and not self.emoji_objects
            and self.letters_to_target == []
        ):
            self.total_destroyed += self.letters_destroyed
            self.current_group_index += 1
            self.just_completed_level = True

            if self.current_group_index < len(self.groups):
                # Start next group
                self.current_group = self.groups[self.current_group_index]
                self.letters_to_spawn = self.current_group.copy()
                self.letters_to_target = self.current_group.copy()
                if self.letters_to_target:
                    self.target_letter = self.letters_to_target[0]
                    self._reset_target_tracking()  # Set up emoji targets for new letter
                else:
                    print(f"Warning: Group {self.current_group_index} is empty.")
                    return False

                # Reset group-specific counters
                self.letters_destroyed = 0
                self.letters_spawned = 0
                self.just_completed_level = False
                self.game_started = True
                self.last_checkpoint_triggered = self.overall_destroyed // 10
            else:
                # All groups completed
                pygame.time.delay(500)
                if not self.checkpoint_manager.show_checkpoint_screen(self.screen, "clcase"):
                    return True  # Exit to menu
                else:
                    return True  # Level complete, return to menu

        return None

    def _draw_frame(self, stars):
        """Draw a complete frame of the C/L Case level."""
        # Apply screen shake if active
        offset_x, offset_y = self.glass_shatter_manager.get_screen_shake_offset()

        # Update glass shatter manager
        self.glass_shatter_manager.update()

        # Fill background based on shatter state
        self.screen.fill(self.glass_shatter_manager.get_background_color())

        # Draw cracks
        self.glass_shatter_manager.draw_cracks(self.screen)

        # Draw background elements (stars)
        self._draw_stars(stars, offset_x, offset_y)

        # Draw center piece (swirl particles + target display)
        self.center_piece_manager.update_and_draw(
            self.screen, self.target_letter, "clcase", offset_x, offset_y
        )

        # Update and draw falling letters and emojis
        self._update_and_draw_letters(offset_x, offset_y)
        self._update_and_draw_emojis(offset_x, offset_y)

        # Process flamethrower effects
        self.flamethrower_manager.update()
        self.flamethrower_manager.draw(self.screen, offset_x, offset_y)

        # Process legacy lasers
        self._process_lasers(offset_x, offset_y)

        # Process explosions
        self._process_explosions(offset_x, offset_y)

        # Draw general particles
        self.particle_manager.update()
        self.particle_manager.draw(self.screen, offset_x, offset_y)

        # Display HUD info
        self.hud_manager.display_info(
            self.screen,
            self.score,
            self.current_ability,
            self.target_letter,
            self.overall_destroyed,
            self.TOTAL_LETTERS,
            "clcase",
        )

    def _draw_stars(self, stars, offset_x, offset_y):
        """Draw and update background stars."""
        for star in stars:
            x, y, radius = star
            y += 1  # Slower star movement speed
            pygame.draw.circle(self.screen, (200, 200, 200), (x + offset_x, y + offset_y), radius)
            if y > self.height + radius:
                y = random.randint(-50, -10)
                x = random.randint(0, self.width)
            star[1] = y
            star[0] = x

    def _update_and_draw_letters(self, offset_x, offset_y):
        """Update and draw falling letters with special clcase handling."""
        for letter_obj in self.letters:
            # Draw the letter
            draw_pos_x = int(letter_obj["x"] + offset_x)
            draw_pos_y = int(letter_obj["y"] + offset_y)

            # Special handling for clcase mode - 'a' becomes 'α'
            display_value = letter_obj["value"]
            if letter_obj["value"] == "a":
                display_value = "α"

            # Use gray for non-target letters, black for the target letter
            text_color = BLACK if letter_obj["value"] == self.target_letter else (150, 150, 150)

            # Use cached font surface if available
            try:
                cached_surface = self.resource_manager.get_falling_object_surface(
                    "clcase", letter_obj["value"], text_color
                )
                text_rect = cached_surface.get_rect(center=(draw_pos_x, draw_pos_y))
                # Inflate rect by 50% for easier interaction (25 pixels on each side)
                interaction_rect = text_rect.inflate(50, 50)
                letter_obj["rect"] = interaction_rect
                self.screen.blit(cached_surface, text_rect)
            except:
                # Fallback: Original rendering method
                text_surface = self.target_font.render(display_value, True, text_color)
                text_rect = text_surface.get_rect(center=(draw_pos_x, draw_pos_y))
                # Inflate rect by 50% for easier interaction (25 pixels on each side)
                interaction_rect = text_rect.inflate(50, 50)
                letter_obj["rect"] = interaction_rect
                self.screen.blit(text_surface, text_rect)

    def _update_and_draw_emojis(self, offset_x, offset_y):
        """Update and draw falling emoji targets."""
        for emoji_obj in self.emoji_objects:
            # Draw the emoji
            draw_pos_x = int(emoji_obj["x"] + offset_x)
            draw_pos_y = int(emoji_obj["y"] + offset_y)

            # Get emoji surface
            emoji_surface = emoji_obj["surface"]
            emoji_rect = emoji_surface.get_rect(center=(draw_pos_x, draw_pos_y))

            # Create interaction rect (slightly larger for easier clicking)
            interaction_rect = emoji_rect.inflate(20, 20)
            emoji_obj["rect"] = interaction_rect

            # Apply visual feedback for current target
            if emoji_obj["letter"] == self.target_letter:
                # Add subtle glow effect for current target emojis
                glow_surface = pygame.Surface(
                    (emoji_rect.width + 10, emoji_rect.height + 10), pygame.SRCALPHA
                )
                glow_color = (*random.choice(FLAME_COLORS), 60)  # Semi-transparent glow
                pygame.draw.rect(
                    glow_surface, glow_color, glow_surface.get_rect(), border_radius=15
                )
                glow_rect = glow_surface.get_rect(center=(draw_pos_x, draw_pos_y))
                self.screen.blit(glow_surface, glow_rect)

            # Draw the emoji
            self.screen.blit(emoji_surface, emoji_rect)

    def _process_lasers(self, offset_x, offset_y):
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

    def _process_explosions(self, offset_x, offset_y):
        """Process explosion effects."""
        for explosion in self.explosions[:]:
            if explosion["duration"] > 0:
                self.draw_explosion(explosion, offset_x, offset_y)
                explosion["duration"] -= 1
            else:
                self.explosions.remove(explosion)
