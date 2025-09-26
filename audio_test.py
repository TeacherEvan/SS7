#!/usr/bin/env python3
"""
Quick audio playback test to verify sounds are audible
"""

import sys
import os
sys.path.append(os.getcwd())
import pygame
import time

pygame.mixer.init()

print("=== AUDIO PLAYBACK TEST ===")
print("Testing if sounds actually play audibly...")

# Test explosion sound first (should be loud)
explosion_path = os.path.join("sounds", "explosion.wav")
if os.path.exists(explosion_path):
    print(f"\n🎵 Playing explosion sound...")
    explosion_sound = pygame.mixer.Sound(explosion_path)
    explosion_sound.play()
    time.sleep(2)
    print("Did you hear the explosion? (Should be loud)")

# Test a letter pronunciation
letter_path = os.path.join("sounds", "a.wav")
if os.path.exists(letter_path):
    print(f"\n🗣️ Playing letter 'A' pronunciation...")
    letter_sound = pygame.mixer.Sound(letter_path)
    letter_sound.play()
    time.sleep(2)
    print("Did you hear the letter 'A'?")

# Test with higher volume
print(f"\n🔊 Testing with maximum volume...")
if os.path.exists(letter_path):
    letter_sound = pygame.mixer.Sound(letter_path)
    letter_sound.set_volume(1.0)  # Maximum volume
    letter_sound.play()
    time.sleep(2)
    print("Did you hear the letter 'A' at full volume?")

print("\n=== Test complete ===")
print("If you didn't hear any sounds, check:")
print("1. Your system volume")
print("2. Your speakers/headphones")
print("3. Windows audio output device")