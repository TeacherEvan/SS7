#!/usr/bin/env python3
"""
Simple sound test to diagnose audio issues
"""
import pygame
import time
import os

def test_sound():
    """Test sound output with different methods"""
    print("Testing sound system...")
    
    # Initialize pygame mixer with different settings
    try:
        pygame.mixer.quit()  # Ensure clean start
    except:
        pass
    
    # Try different audio settings
    print("Initializing pygame mixer...")
    pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=1024)
    pygame.mixer.init()
    
    print(f"Mixer initialized: {pygame.mixer.get_init()}")
    print(f"Number of channels: {pygame.mixer.get_num_channels()}")
    
    # Test 1: Load and play explosion sound
    if os.path.exists("sounds/explosion.wav"):
        print("\nTest 1: Playing explosion.wav...")
        sound = pygame.mixer.Sound("sounds/explosion.wav")
        sound.set_volume(1.0)  # Maximum volume
        print(f"Sound loaded, volume: {sound.get_volume()}")
        sound.play()
        time.sleep(2)
        print("Explosion sound test complete")
    else:
        print("ERROR: sounds/explosion.wav not found!")
    
    # Test 2: Generate a simple beep
    print("\nTest 2: Generating simple beep...")
    import numpy as np
    
    # Generate a 440Hz tone (A note)
    sample_rate = 22050
    duration = 1.0
    frequency = 440
    
    frames = int(duration * sample_rate)
    arr = np.zeros((frames, 2))
    
    for i in range(frames):
        wave = np.sin(2 * np.pi * frequency * i / sample_rate)
        arr[i] = [wave, wave]
    
    # Convert to pygame sound
    arr = (arr * 32767).astype(np.int16)
    beep_sound = pygame.sndarray.make_sound(arr)
    beep_sound.set_volume(0.8)
    
    print("Playing generated beep...")
    beep_sound.play()
    time.sleep(2)
    print("Beep test complete")
    
    # Test 3: Check if sounds are actually playing
    print(f"\nActive channels: {pygame.mixer.get_busy()}")
    
    print("\nSound test finished. Did you hear any sounds?")

if __name__ == "__main__":
    test_sound()