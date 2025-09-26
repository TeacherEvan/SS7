"""
Quick test to verify emoji spawning logic works correctly
"""

import os
import sys

import pygame

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import settings
from levels.alphabet_level import AlphabetLevel
from universal_class import *
from utils.resource_manager import ResourceManager


def test_emoji_spawning():
    """Test the emoji spawning logic"""
    pygame.init()

    # Create minimal setup
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))

    # Create mock objects
    resource_manager = ResourceManager()
    resource_manager.set_display_mode("DEFAULT")
    fonts = resource_manager.initialize_game_resources()

    # Create minimal alphabet level
    level = AlphabetLevel(
        width,
        height,
        screen,
        fonts["fonts"],
        fonts["small_font"],
        fonts["target_font"],
        None,
        None,
        None,
        None,
        None,
        None,
        None,  # Mock managers
        resource_manager,
        None,
        None,
        None,
        None,  # Mock functions
        [],
        [],
        None,
        None,
        None,  # Mock lists and functions
    )

    print(f"Initial target letter: {level.target_letter}")
    print(f"Targets needed: {level.targets_needed}")
    print(f"Current hits: {level.current_target_hits}")

    # Check if emojis are available
    if level.target_letter:
        emojis = resource_manager.get_letter_emojis(level.target_letter)
        print(f"Emojis available for {level.target_letter}: {len(emojis)}")

        # Simulate frame updates to test spawning
        for frame in range(120):  # 2 seconds at 60fps
            level.frame_count = frame
            level._ensure_target_emojis_available()

            if frame % 60 == 0:  # Check every second
                objects = [obj["value"] for obj in level.letters]
                print(f"Frame {frame}: Objects on screen: {objects}")

    pygame.quit()
    print("✅ Emoji spawning test completed!")


if __name__ == "__main__":
    test_emoji_spawning()
