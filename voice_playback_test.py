#!/usr/bin/env python3
"""
Test voice playback in SS6
"""

import os
import sys
import time

sys.path.append(os.getcwd())
import pygame

from universal_class import SoundManager

pygame.init()

print("=== VOICE PLAYBACK TEST ===")
sound_manager = SoundManager()
print(f"Sound Manager Initialized: {sound_manager.initialized}")

# Test voice playback
print("\n=== TESTING VOICE PLAYBACK ===")
test_voices = ["A", "B", "C", "1", "2", "red", "circle"]

for voice in test_voices:
    print(f"\nTesting voice: {voice}")
    success = sound_manager.play_voice(voice)
    print(f'Play result: {"✓ Success" if success else "✗ Failed"}')

    if success:
        print("Voice should be playing now...")
        time.sleep(2)  # Give time for voice to play
    else:
        print("Voice failed to play")

print("\n=== TEST COMPLETE ===")
