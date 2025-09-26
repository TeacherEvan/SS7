import os
from pathlib import Path

import pygame

from Display_settings import FONT_SIZES
from settings import BLACK, FLAME_COLORS, SEQUENCES, WHITE


class ResourceManager:
    """Manages game resources like fonts and emoji images based on display mode."""

    def __init__(self):
        self.display_mode = "DEFAULT"
        self.fonts = {}
        self.large_font = None
        self.small_font = None
        self.target_font = None
        self.title_font = None

        # Font caches for performance optimization
        self.center_target_cache = {}  # Cache for center target (size 900)
        self.falling_object_cache = {}  # Cache for falling objects (size 240)
        self.center_font = None  # Font for center target (size 900)
        self.falling_font = None  # Font for falling objects (size 240)

        # Emoji caches for alphabet level
        self.emoji_cache = {}  # Cache for emoji surfaces
        self.emoji_associations = self._load_emoji_associations()
        self.assets_dir = Path(__file__).parent.parent / "assets" / "emojis"

    def set_display_mode(self, mode):
        """Set the current display mode."""
        self.display_mode = mode

    def initialize_game_resources(self):
        """Initialize fonts and other resources based on display mode."""
        # Get font sizes for current display mode
        font_sizes = FONT_SIZES[self.display_mode]["regular"]
        large_font_size = FONT_SIZES[self.display_mode]["large"]

        # Initialize fonts
        self.fonts = [
            pygame.font.Font(None, font_sizes),
            pygame.font.Font(None, int(font_sizes * 1.5)),
            pygame.font.Font(None, int(font_sizes * 2)),
            pygame.font.Font(None, int(font_sizes * 2.5)),
            pygame.font.Font(None, int(font_sizes * 3)),
        ]

        self.large_font = pygame.font.Font(None, large_font_size)
        self.small_font = pygame.font.Font(None, font_sizes)
        self.target_font = pygame.font.Font(
            None, int(font_sizes * 8)
        )  # Large font for targets (doubled from 4 to 8)
        self.title_font = pygame.font.Font(None, int(font_sizes * 8))  # Very large for titles

        # Initialize performance-critical fonts
        self.center_font = pygame.font.Font(None, 900)  # Center target font
        self.falling_font = pygame.font.Font(None, 240)  # Falling objects font

        # Pre-cache commonly used text surfaces
        self._initialize_font_caches()

        # Pre-cache emoji surfaces for alphabet level
        self._initialize_emoji_caches()

        return {
            "fonts": self.fonts,
            "large_font": self.large_font,
            "small_font": self.small_font,
            "target_font": self.target_font,
            "title_font": self.title_font,
            "center_font": self.center_font,
            "falling_font": self.falling_font,
        }

    def _initialize_font_caches(self):
        """Pre-render commonly used text surfaces for performance."""
        print(f"Initializing font caches for display mode: {self.display_mode}")

        # Clear existing caches
        self.center_target_cache.clear()
        self.falling_object_cache.clear()

        # Cache center target surfaces (size 900) for all game modes
        self._cache_center_targets()

        # Cache falling object surfaces (size 240) for all game modes
        self._cache_falling_objects()

        print(
            f"Font cache initialized: {len(self.center_target_cache)} center targets, {len(self.falling_object_cache)} falling objects"
        )

    def _cache_center_targets(self):
        """Pre-render center target text surfaces."""
        # Colors for center targets (flame colors for text modes)
        center_colors = FLAME_COLORS + [BLACK]  # Include black for shapes mode

        # Cache all sequences for center targets
        for mode, sequence in SEQUENCES.items():
            if mode == "shapes":
                continue  # Shapes don't use text for center targets

            for item in sequence:
                for color in center_colors:
                    # Handle special cases
                    display_char = item
                    if mode == "clcase":
                        display_char = item.upper()
                    elif (mode == "alphabet" or mode == "clcase") and item == "a":
                        display_char = "α"

                    cache_key = (mode, item, color)
                    if cache_key not in self.center_target_cache:
                        surface = self.center_font.render(display_char, True, color)
                        self.center_target_cache[cache_key] = surface

    def _cache_falling_objects(self):
        """Pre-render falling object text surfaces."""
        # Colors for falling objects
        falling_colors = [BLACK, (150, 150, 150)]  # Target and non-target colors

        # Cache all sequences for falling objects
        for mode, sequence in SEQUENCES.items():
            if mode == "shapes":
                continue  # Shapes don't use text for falling objects

            for item in sequence:
                for color in falling_colors:
                    # Handle special cases
                    display_char = item
                    if mode == "clcase" and item == "a":
                        display_char = "α"

                    cache_key = (mode, item, color)
                    if cache_key not in self.falling_object_cache:
                        surface = self.falling_font.render(display_char, True, color)
                        self.falling_object_cache[cache_key] = surface

    def get_center_target_surface(self, mode, target_letter, color):
        """Get cached center target surface or render if not cached."""
        cache_key = (mode, target_letter, color)

        if cache_key in self.center_target_cache:
            return self.center_target_cache[cache_key]

        # Fallback: render on demand and cache
        display_char = target_letter
        if mode == "clcase":
            display_char = target_letter.upper()
        elif (mode == "alphabet" or mode == "clcase") and target_letter == "a":
            display_char = "α"

        surface = self.center_font.render(display_char, True, color)
        self.center_target_cache[cache_key] = surface
        return surface

    def get_falling_object_surface(self, mode, item_value, color):
        """Get cached falling object surface or render if not cached."""
        cache_key = (mode, item_value, color)

        if cache_key in self.falling_object_cache:
            return self.falling_object_cache[cache_key]

        # Fallback: render on demand and cache
        display_char = item_value
        if mode == "clcase" and item_value == "a":
            display_char = "α"

        surface = self.falling_font.render(display_char, True, color)
        self.falling_object_cache[cache_key] = surface
        return surface

    def clear_caches(self):
        """Clear all font caches to free memory."""
        self.center_target_cache.clear()
        self.falling_object_cache.clear()
        self.emoji_cache.clear()

    def get_cache_stats(self):
        """Get statistics about cache usage."""
        return {
            "center_targets": len(self.center_target_cache),
            "falling_objects": len(self.falling_object_cache),
            "emojis": len(self.emoji_cache),
            "total_cached_surfaces": len(self.center_target_cache)
            + len(self.falling_object_cache)
            + len(self.emoji_cache),
        }

    def _load_emoji_associations(self):
        """Load the emoji associations for each letter."""
        return {
            "A": ["apple", "ant"],
            "B": ["ball", "banana"],
            "C": ["cat", "car"],
            "D": ["dog", "duck"],
            "E": ["elephant", "egg"],
            "F": ["fish", "flower"],
            "G": ["giraffe", "grapes"],
            "H": ["house", "hat"],
            "I": ["ice_cream", "iguana"],
            "J": ["jar", "juice"],
            "K": ["kite", "key"],
            "L": ["lion", "leaf"],
            "M": ["mouse", "moon"],
            "N": ["nest", "nose"],
            "O": ["orange", "owl"],
            "P": ["penguin", "pizza"],
            "Q": ["queen", "question_mark"],
            "R": ["rainbow", "rabbit"],
            "S": ["sun", "snake"],
            "T": ["tree", "tiger"],
            "U": ["umbrella", "unicorn"],
            "V": ["violin", "volcano"],
            "W": ["whale", "watermelon"],
            "X": ["x-ray", "xylophone"],
            "Y": ["yarn", "yacht"],
            "Z": ["zebra", "zipper"],
        }

    def _initialize_emoji_caches(self):
        """Pre-load and cache emoji surfaces for performance."""
        if not self.assets_dir.exists():
            print(f"Warning: Emoji assets directory not found: {self.assets_dir}")
            return

        print("Loading emoji assets...")
        loaded_count = 0

        # Calculate emoji size based on display mode
        emoji_size = self._get_emoji_size()

        for letter, emojis in self.emoji_associations.items():
            for i, emoji_name in enumerate(emojis, 1):
                filename = f"{letter}_{emoji_name}_{i}.png"
                filepath = self.assets_dir / filename

                if filepath.exists():
                    try:
                        # Load and scale emoji surface
                        original_surface = pygame.image.load(str(filepath)).convert_alpha()
                        # pygame.transform.smoothscale provides high-quality image scaling
                        scaled_surface = pygame.transform.smoothscale(original_surface, emoji_size)

                        # Cache the scaled surface
                        cache_key = (letter, i)
                        self.emoji_cache[cache_key] = scaled_surface
                        loaded_count += 1

                    except Exception as e:
                        print(f"Warning: Failed to load emoji {filename}: {e}")
                else:
                    print(f"Warning: Emoji file not found: {filename}")

        print(f"Loaded {loaded_count} emoji assets")

    def _get_emoji_size(self):
        """Get emoji size based on display mode."""
        # Scale emoji size based on display mode
        if self.display_mode == "QBOARD":
            return (64, 64)  # Smaller for QBoard performance
        else:
            return (96, 96)  # Standard size for regular displays

    def get_letter_emojis(self, letter):
        """Get both emoji surfaces for a given letter (handles both uppercase and lowercase)."""
        # Convert to uppercase for emoji lookup since emoji filenames use uppercase
        letter_key = letter.upper()
        if letter_key not in self.emoji_associations:
            return []

        emojis = []
        for i in range(1, 3):  # Get emoji 1 and 2
            cache_key = (letter_key, i)
            if cache_key in self.emoji_cache:
                emojis.append(self.emoji_cache[cache_key])

        return emojis

    def has_emojis_for_letter(self, letter):
        """Check if emojis are available for a given letter (handles both uppercase and lowercase)."""
        # Convert to uppercase for emoji lookup since emoji filenames use uppercase
        letter_key = letter.upper()
        return letter_key in self.emoji_associations and any(
            (letter_key, i) in self.emoji_cache for i in range(1, 3)
        )
