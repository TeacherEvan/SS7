#!/usr/bin/env python3
"""
Comprehensive Sound File Generator for SS6 Super Student Game
Generates all necessary sound files for commit to repository.
"""

import os
import time

from utils.contextual_voice_generator import ContextAwareVoiceGenerator
from utils.voice_assignment import ContentType, LevelType, VoiceAssignmentSystem


class GameSoundGenerator:
    """
    Generates all sound files needed for the SS6 game with proper voice assignments.
    """

    def __init__(self):
        """Initialize the sound generator."""
        self.cvg = ContextAwareVoiceGenerator()
        self.vas = VoiceAssignmentSystem()
        self.sounds_dir = "sounds"
        self.generated_files = []
        self.failed_files = []

        # Ensure sounds directory exists
        os.makedirs(self.sounds_dir, exist_ok=True)

    def generate_alphabet_sounds(self):
        """Generate all alphabet letter sounds (A-Z)."""
        print("🔤 Generating Alphabet Sounds...")
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

        for letter in alphabet:
            success = self.cvg.generate_letter_voice(letter, LevelType.ALPHABET)
            if success:
                self.generated_files.append(f"{letter.lower()}.wav")
                print(f"✅ Generated: {letter}")
            else:
                self.failed_files.append(f"{letter.lower()}.wav")
                print(f"❌ Failed: {letter}")
            time.sleep(0.5)  # Small delay to avoid rate limiting

    def generate_emoji_sounds(self):
        """Generate emoji pronunciation sounds for alphabet levels."""
        print("\n🎭 Generating Emoji Pronunciation Sounds...")

        # Standard letter-emoji associations
        emoji_associations = {
            "A": ["apple", "ant"],
            "B": ["ball", "banana"],
            "C": ["cat", "car"],
            "D": ["dog", "duck"],
            "E": ["elephant", "egg"],
            "F": ["fish", "flower"],
            "G": ["giraffe", "grapes"],
            "H": ["house", "hat"],
            "I": ["ice cream", "iguana"],
            "J": ["jar", "juice"],
            "K": ["kite", "key"],
            "L": ["lion", "leaf"],
            "M": ["mouse", "moon"],
            "N": ["nest", "nose"],
            "O": ["orange", "owl"],
            "P": ["penguin", "pizza"],
            "Q": ["queen", "question mark"],
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

        for letter, emojis in emoji_associations.items():
            for emoji in emojis:
                success = self.cvg.generate_emoji_voice(emoji, LevelType.ALPHABET)
                filename = f"emoji_{emoji.lower().replace(' ', '_').replace('-', '_')}.wav"
                if success:
                    self.generated_files.append(filename)
                    print(f"✅ Generated emoji: {emoji} (for {letter})")
                else:
                    self.failed_files.append(filename)
                    print(f"❌ Failed emoji: {emoji} (for {letter})")
                time.sleep(0.5)

    def generate_number_sounds(self):
        """Generate number sounds (1-10)."""
        print("\n🔢 Generating Number Sounds...")

        for number in range(1, 11):
            success = self.cvg.generate_number_voice(str(number))
            if success:
                self.generated_files.append(f"{number}.wav")
                print(f"✅ Generated: {number}")
            else:
                self.failed_files.append(f"{number}.wav")
                print(f"❌ Failed: {number}")
            time.sleep(0.5)

    def generate_color_sounds(self):
        """Generate color sounds with appropriate voice distribution."""
        print("\n🎨 Generating Color Sounds...")
        colors = [
            "red",
            "blue",
            "green",
            "yellow",
            "purple",
            "orange",
            "pink",
            "brown",
            "black",
            "white",
        ]

        for color in colors:
            success = self.cvg.generate_target_hit_voice(color, LevelType.COLORS)
            if success:
                self.generated_files.append(f"{color}.wav")
                # Check which voice was selected
                voice_key, _ = self.vas.get_voice_for_content(
                    LevelType.COLORS, ContentType.TARGET_HIT, color, "target_destroyed"
                )
                voice_type = "Male" if voice_key == "male_elderly_stoic" else "Female"
                print(f"✅ Generated: {color} ({voice_type})")
            else:
                self.failed_files.append(f"{color}.wav")
                print(f"❌ Failed: {color}")
            time.sleep(0.5)

    def generate_shape_sounds(self):
        """Generate shape sounds with appropriate voice distribution."""
        print("\n⭕ Generating Shape Sounds...")
        shapes = [
            "circle",
            "square",
            "triangle",
            "rectangle",
            "pentagon",
            "hexagon",
            "oval",
            "diamond",
        ]

        for shape in shapes:
            success = self.cvg.generate_target_hit_voice(shape, LevelType.SHAPES)
            if success:
                self.generated_files.append(f"{shape}.wav")
                # Check which voice was selected
                voice_key, _ = self.vas.get_voice_for_content(
                    LevelType.SHAPES, ContentType.TARGET_HIT, shape, "target_destroyed"
                )
                voice_type = "Male" if voice_key == "male_elderly_stoic" else "Female"
                print(f"✅ Generated: {shape} ({voice_type})")
            else:
                self.failed_files.append(f"{shape}.wav")
                print(f"❌ Failed: {shape}")
            time.sleep(0.5)

    def generate_welcome_messages(self):
        """Generate welcome messages with both voices."""
        print("\n🎉 Generating Welcome Messages...")

        welcome_text = "Welcome to Teacher Evan's Super Student. Let's have fun learning together!"

        # Generate with female voice
        success_female = self.cvg.generate_general_voice(
            welcome_text, "welcome_female", LevelType.ALPHABET
        )
        if success_female:
            self.generated_files.append("welcome_female.wav")
            print("✅ Generated: Welcome message (Female - Rachel)")
        else:
            self.failed_files.append("welcome_female.wav")
            print("❌ Failed: Welcome message (Female)")

        time.sleep(1)

        # Generate with male voice by temporarily forcing the assignment
        # We'll generate it as an emoji to trigger male voice selection
        success_male = self.cvg.generate_emoji_voice("welcome_message", LevelType.ALPHABET)
        if success_male:
            # Rename the file from emoji_welcome_message.wav to welcome_male.wav
            old_path = os.path.join(self.sounds_dir, "emoji_welcome_message.wav")
            new_path = os.path.join(self.sounds_dir, "welcome_male.wav")
            if os.path.exists(old_path):
                os.rename(old_path, new_path)
                self.generated_files.append("welcome_male.wav")
                print("✅ Generated: Welcome message (Male - Elderly Stoic)")

        if not success_male:
            # Alternative: Generate directly with male voice settings
            try:
                voice_config = self.vas.available_voices["male_elderly_stoic"]
                success_male_alt = self.cvg._generate_with_voice(
                    welcome_text,
                    "welcome_male",
                    voice_config["id"],
                    voice_config.get("settings", {}),
                    voice_config.get("name", "Male Voice"),
                )
                if success_male_alt:
                    self.generated_files.append("welcome_male.wav")
                    print(
                        "✅ Generated: Welcome message (Male - Elderly Stoic) [Alternative method]"
                    )
                else:
                    self.failed_files.append("welcome_male.wav")
                    print("❌ Failed: Welcome message (Male)")
            except Exception as e:
                self.failed_files.append("welcome_male.wav")
                print(f"❌ Failed: Welcome message (Male) - {e}")

    def generate_case_level_sounds(self):
        """Generate lowercase letter sounds for case level."""
        print("\n🔠 Generating Case Level Sounds...")
        alphabet = "abcdefghijklmnopqrstuvwxyz"

        for letter in alphabet:
            # Check if uppercase version already exists (they might be the same file)
            uppercase_file = f"{letter.upper().lower()}.wav"  # This is just letter.lower()
            if uppercase_file not in self.generated_files:
                success = self.cvg.generate_letter_voice(letter, LevelType.CL_CASE)
                if success:
                    self.generated_files.append(f"{letter}.wav")
                    print(f"✅ Generated case: {letter}")
                else:
                    self.failed_files.append(f"{letter}.wav")
                    print(f"❌ Failed case: {letter}")
                time.sleep(0.5)
            else:
                print(f"⚡ Skipped: {letter} (already generated)")

    def generate_all_sounds(self):
        """Generate all sound files for the game."""
        print("🎵 SS6 Comprehensive Sound File Generator")
        print("=" * 60)
        print("Generating all sound files for repository commit...")
        print("This ensures offline functionality without API requirements.\n")

        start_time = time.time()

        # Generate all sound categories
        self.generate_alphabet_sounds()
        self.generate_case_level_sounds()
        self.generate_emoji_sounds()
        self.generate_number_sounds()
        self.generate_color_sounds()
        self.generate_shape_sounds()
        self.generate_welcome_messages()

        # Generate summary
        end_time = time.time()
        duration = end_time - start_time

        print(f"\n🎉 Sound Generation Complete!")
        print("=" * 60)
        print(f"⏱️  Total time: {duration:.1f} seconds")
        print(f"✅ Successfully generated: {len(self.generated_files)} files")
        print(f"❌ Failed to generate: {len(self.failed_files)} files")

        if self.failed_files:
            print(f"\n⚠️  Failed files:")
            for failed_file in self.failed_files:
                print(f"   • {failed_file}")

        print(f"\n📁 All sound files saved to: {os.path.abspath(self.sounds_dir)}")
        print("🚀 Ready for repository commit!")

        return len(self.generated_files), len(self.failed_files)


def main():
    """Generate all game sound files."""
    generator = GameSoundGenerator()
    successful, failed = generator.generate_all_sounds()

    if failed == 0:
        print("\n🎯 Perfect! All sound files generated successfully!")
    else:
        print(f"\n⚠️  {failed} files failed to generate. Check API connectivity.")

    return successful > 0


if __name__ == "__main__":
    main()
