import pygame
import sys
import os

def test_sound(sound_file):
    """Test if a specific sound file can be played."""
    print(f"Testing sound file: {sound_file}")
    
    # Initialize pygame mixer
    pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
    pygame.mixer.init()
    
    if not os.path.exists(sound_file):
        print(f"ERROR: Sound file not found: {sound_file}")
        return False
    
    try:
        # Load the sound
        sound = pygame.mixer.Sound(sound_file)
        print(f"Sound loaded successfully. Length: {sound.get_length():.2f} seconds")
        
        # Set volume
        sound.set_volume(0.8)
        
        # Play the sound
        print("Playing sound...")
        channel = sound.play()
        
        # Wait for sound to finish
        while channel.get_busy():
            pygame.time.wait(100)
        
        print("Sound finished playing.")
        return True
        
    except pygame.error as e:
        print(f"Pygame error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False
    finally:
        pygame.mixer.quit()

if __name__ == "__main__":
    # Test multiple sound files
    test_files = [
        "sounds/1.wav",
        "sounds/a.wav", 
        "sounds/explosion.wav",
        "sounds/red.wav"
    ]
    
    for file in test_files:
        print(f"\n{'='*50}")
        test_sound(file)
        input("Press Enter to continue to next sound...")