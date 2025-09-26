#!/usr/bin/env python3
"""
Quick TTS Test - Simple command line tool for testing custom text with current voice
"""

import sys

import pygame

from utils.voice_generator import UniversalVoiceGenerator


def test_custom_text(text):
    """Test custom text with current voice configuration."""
    print(f"🎤 Testing TTS with: '{text}'")
    print("=" * 60)

    pygame.mixer.init()
    vg = UniversalVoiceGenerator()

    # Generate voice
    filename = "quick_test"
    result = vg.generate_voice_file(text, filename)

    if result:
        print("✅ Voice generation successful!")

        # Play the generated voice
        try:
            sound_file = f"sounds/{filename}.wav"
            sound = pygame.mixer.Sound(sound_file)
            print("🔊 Playing generated speech...")
            sound.play()
            pygame.time.wait(len(text) * 100 + 2000)  # Estimate playback time
            print("✅ Playback complete!")
            return True
        except Exception as e:
            print(f"❌ Playback error: {e}")
            return False
    else:
        print("❌ Voice generation failed!")
        return False


def main():
    if len(sys.argv) > 1:
        # Use command line argument
        text = " ".join(sys.argv[1:])
    else:
        # Interactive input
        text = input("Enter text to speak: ").strip()

    if not text:
        print("❌ No text provided!")
        return

    success = test_custom_text(text)

    if success:
        print("\n🎉 TTS test completed successfully!")
    else:
        print("\n❌ TTS test failed!")


if __name__ == "__main__":
    main()
