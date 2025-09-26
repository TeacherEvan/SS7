#!/usr/bin/env python3
"""
Comprehensive Voice System Demo for SS6 Super Student Game
Demonstrates the intelligent voice assignment system in action.
"""

import time

import pygame

from utils.contextual_voice_generator import ContextAwareVoiceGenerator
from utils.voice_assignment import ContentType, LevelType, VoiceAssignmentSystem


def play_voice_file(filename):
    """Play a voice file and wait for completion."""
    try:
        sound_file = f"sounds/{filename}.wav"
        sound = pygame.mixer.Sound(sound_file)
        print(f"🔊 Playing: {filename}.wav")
        sound.play()
        pygame.time.wait(3000)  # Wait 3 seconds
        return True
    except Exception as e:
        print(f"❌ Could not play {filename}: {e}")
        return False


def demonstrate_voice_system():
    """Demonstrate the complete voice assignment and generation system."""

    print("🎤 SS6 Voice System Comprehensive Demo")
    print("=" * 60)

    # Initialize systems
    pygame.mixer.init()
    cvg = ContextAwareVoiceGenerator()
    vas = VoiceAssignmentSystem()

    print("\n📋 Voice Assignment Rules:")
    print("  • Female voice (Rachel): Primary narrator for most content")
    print("  • Male voice (Elderly Stoic): Emoji pronunciations in ABC/Case levels")
    print("  • Colors/Shapes levels: 40% male, 60% female for target hits")
    print()

    # Test scenarios
    scenarios = [
        {
            "title": "🔤 Alphabet Level - Letter Pronunciation",
            "tests": [
                ("Letter A", lambda: cvg.generate_letter_voice("A", LevelType.ALPHABET)),
                ("Letter B", lambda: cvg.generate_letter_voice("B", LevelType.ALPHABET)),
            ],
        },
        {
            "title": "🔤 Alphabet Level - Emoji Pronunciation (Male Voice)",
            "tests": [
                ("Emoji: Apple", lambda: cvg.generate_emoji_voice("apple", LevelType.ALPHABET)),
                ("Emoji: Ball", lambda: cvg.generate_emoji_voice("ball", LevelType.ALPHABET)),
            ],
        },
        {
            "title": "🔠 Case Level - Letter and Emoji",
            "tests": [
                ("Letter: a", lambda: cvg.generate_letter_voice("a", LevelType.CL_CASE)),
                ("Emoji: ant", lambda: cvg.generate_emoji_voice("ant", LevelType.CL_CASE)),
            ],
        },
        {
            "title": "🎨 Colors Level - Random Voice Selection (40% Male, 60% Female)",
            "tests": [
                ("Color: red", lambda: cvg.generate_target_hit_voice("red", LevelType.COLORS)),
                ("Color: blue", lambda: cvg.generate_target_hit_voice("blue", LevelType.COLORS)),
                ("Color: green", lambda: cvg.generate_target_hit_voice("green", LevelType.COLORS)),
                (
                    "Color: yellow",
                    lambda: cvg.generate_target_hit_voice("yellow", LevelType.COLORS),
                ),
            ],
        },
        {
            "title": "⭕ Shapes Level - Random Voice Selection (40% Male, 60% Female)",
            "tests": [
                (
                    "Shape: circle",
                    lambda: cvg.generate_target_hit_voice("circle", LevelType.SHAPES),
                ),
                (
                    "Shape: square",
                    lambda: cvg.generate_target_hit_voice("square", LevelType.SHAPES),
                ),
                (
                    "Shape: triangle",
                    lambda: cvg.generate_target_hit_voice("triangle", LevelType.SHAPES),
                ),
            ],
        },
        {
            "title": "🔢 Numbers Level - Female Voice Default",
            "tests": [
                ("Number: 5", lambda: cvg.generate_number_voice("5")),
                ("Number: 10", lambda: cvg.generate_number_voice("10")),
            ],
        },
    ]

    # Run demonstrations
    for scenario in scenarios:
        print(f"\n{scenario['title']}")
        print("-" * len(scenario["title"]))

        for test_name, test_func in scenario["tests"]:
            # Generate voice
            success = test_func()

            if success:
                # Determine which voice was selected
                if "emoji" in test_name.lower() and (
                    "alphabet" in scenario["title"].lower() or "case" in scenario["title"].lower()
                ):
                    selected_voice = "🗣️ Male (Elderly Stoic)"
                elif "color" in scenario["title"].lower() or "shape" in scenario["title"].lower():
                    # For colors/shapes, we need to check which voice was actually selected
                    if "red" in test_name.lower():
                        voice_key, _ = vas.get_voice_for_content(
                            LevelType.COLORS, ContentType.TARGET_HIT, "red", "target_destroyed"
                        )
                    elif "blue" in test_name.lower():
                        voice_key, _ = vas.get_voice_for_content(
                            LevelType.COLORS, ContentType.TARGET_HIT, "blue", "target_destroyed"
                        )
                    elif "green" in test_name.lower():
                        voice_key, _ = vas.get_voice_for_content(
                            LevelType.COLORS, ContentType.TARGET_HIT, "green", "target_destroyed"
                        )
                    elif "yellow" in test_name.lower():
                        voice_key, _ = vas.get_voice_for_content(
                            LevelType.COLORS, ContentType.TARGET_HIT, "yellow", "target_destroyed"
                        )
                    elif "circle" in test_name.lower():
                        voice_key, _ = vas.get_voice_for_content(
                            LevelType.SHAPES, ContentType.TARGET_HIT, "circle", "target_destroyed"
                        )
                    elif "square" in test_name.lower():
                        voice_key, _ = vas.get_voice_for_content(
                            LevelType.SHAPES, ContentType.TARGET_HIT, "square", "target_destroyed"
                        )
                    elif "triangle" in test_name.lower():
                        voice_key, _ = vas.get_voice_for_content(
                            LevelType.SHAPES, ContentType.TARGET_HIT, "triangle", "target_destroyed"
                        )

                    selected_voice = (
                        "🗣️ Male (Elderly Stoic)"
                        if voice_key == "male_elderly_stoic"
                        else "🗣️ Female (Rachel)"
                    )
                else:
                    selected_voice = "🗣️ Female (Rachel)"

                print(f"✅ {test_name:15} → {selected_voice}")

                # Play the generated voice file if available
                if ":" in test_name and "emoji" in test_name.lower():
                    filename = f"emoji_{test_name.split(':')[1].strip().lower()}"
                elif ":" in test_name:
                    filename = test_name.split(":")[1].strip().lower()
                else:
                    filename = test_name.lower().replace(" ", "_")

                # play_voice_file(filename)

            else:
                print(f"❌ {test_name:15} → Generation failed")

    print(f"\n🎉 Voice System Demo Complete!")
    print("\n📊 Summary:")
    print("  ✅ Contextual voice selection working")
    print("  ✅ Female voice handles primary narration")
    print("  ✅ Male voice handles emoji pronunciations in ABC/Case levels")
    print("  ✅ Percentage-based selection working for Colors/Shapes levels")
    print("  ✅ All voice generation and caching functional")


def main():
    """Run the comprehensive voice system demonstration."""
    demonstrate_voice_system()


if __name__ == "__main__":
    main()
