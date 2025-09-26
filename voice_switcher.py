#!/usr/bin/env python3
"""
Voice Switcher Utility for SS6 Super Student Game
Allows easy switching between available voices and testing them.
"""

import json
import os
import pygame
from utils.voice_generator import UniversalVoiceGenerator

class VoiceSwitcher:
    def __init__(self):
        self.config_path = os.path.join("config", "voice_config.json")
        self.config = self.load_config()
        pygame.mixer.init()
        
    def load_config(self):
        """Load voice configuration."""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}
    
    def save_config(self):
        """Save voice configuration."""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def list_voices(self):
        """List all available voices."""
        print("\n=== Available Voices ===")
        voices = self.config.get('available_voices', {})
        current_voice = self.config.get('current_voice', 'female_default')
        
        for key, voice in voices.items():
            marker = "🎤 CURRENT" if key == current_voice else "  "
            print(f"{marker} {key}: {voice['name']}")
            print(f"     Description: {voice['description']}")
            print(f"     ID: {voice['id']}")
            print()
    
    def switch_voice(self, voice_key):
        """Switch to a specific voice."""
        voices = self.config.get('available_voices', {})
        
        if voice_key not in voices:
            print(f"❌ Voice '{voice_key}' not found!")
            print("Available voices:", list(voices.keys()))
            return False
        
        voice = voices[voice_key]
        
        # Update main voice configuration
        self.config['current_voice'] = voice_key
        self.config['voice_id'] = voice['id']
        self.config['voice_settings'].update(voice['settings'])
        self.config['voice_description'] = voice['description']
        
        if self.save_config():
            print(f"✅ Switched to voice: {voice['name']}")
            print(f"   Description: {voice['description']}")
            return True
        else:
            print("❌ Failed to save configuration")
            return False
    
    def test_voice(self, voice_key=None, test_text=None):
        """Test a voice with sample text."""
        if voice_key:
            self.switch_voice(voice_key)
        
        if not test_text:
            test_text = "Welcome to Super Student Six. Let us begin learning together."
        
        print(f"🎵 Testing voice with: '{test_text}'")
        
        vg = UniversalVoiceGenerator()
        filename = f"voice_test_{self.config.get('current_voice', 'default')}"
        
        if vg.generate_voice_file(test_text, filename):
            print("✅ Voice generated successfully!")
            
            # Play the generated voice
            try:
                sound_file = f"sounds/{filename}.wav"
                if os.path.exists(sound_file):
                    sound = pygame.mixer.Sound(sound_file)
                    print("🔊 Playing sample...")
                    sound.play()
                    pygame.time.wait(6000)  # Wait for playback
                    print("✅ Playback complete!")
                else:
                    print(f"❌ Generated file not found: {sound_file}")
            except Exception as e:
                print(f"❌ Playback error: {e}")
        else:
            print("❌ Voice generation failed")
    
    def interactive_menu(self):
        """Interactive voice switching menu."""
        while True:
            print("\n" + "="*50)
            print("🎤 SS6 Voice Switcher")
            print("="*50)
            
            self.list_voices()
            
            print("Options:")
            print("1. Switch to female voice")
            print("2. Switch to male elderly stoic voice")  
            print("3. Test current voice")
            print("4. Test with custom text")
            print("0. Exit")
            
            choice = input("\nEnter your choice (0-4): ").strip()
            
            if choice == "0":
                print("👋 Goodbye!")
                break
            elif choice == "1":
                self.switch_voice("female_default")
            elif choice == "2":
                self.switch_voice("male_elderly_stoic")
            elif choice == "3":
                self.test_voice()
            elif choice == "4":
                custom_text = input("Enter text to test: ").strip()
                if custom_text:
                    self.test_voice(test_text=custom_text)
            else:
                print("❌ Invalid choice. Please try again.")

def main():
    """Main function."""
    print("🎤 SS6 Voice Switcher Utility")
    print("Manage and test voices for your Super Student game!")
    
    switcher = VoiceSwitcher()
    switcher.interactive_menu()

if __name__ == "__main__":
    main()