#!/usr/bin/env python3
"""
Context-Aware Voice Generator for SS6 Super Student Game
Integrates with the voice assignment system to automatically select appropriate voices.
"""

import os
import json
import requests
import pygame
from typing import Dict, Optional, Tuple
import logging

from utils.voice_assignment import VoiceAssignmentSystem, ContentType, LevelType

class ContextAwareVoiceGenerator:
    """
    Voice generator that automatically selects the appropriate voice based on context.
    """
    
    def __init__(self):
        """Initialize the context-aware voice generator."""
        self.assignment_system = VoiceAssignmentSystem()
        self.config = self.assignment_system.config
        self.api_key = self._get_api_key()
        self.base_url = "https://api.elevenlabs.io/v1"
        self.sounds_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sounds")
        
        # Ensure sounds directory exists
        os.makedirs(self.sounds_dir, exist_ok=True)
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        self.logger.info("Context-aware voice generator initialized")
        
    def _get_api_key(self) -> Optional[str]:
        """Get ElevenLabs API key from config."""
        return self.config.get('elevenlabs_api_key')
    
    def generate_contextual_voice(self, 
                                text: str, 
                                filename: str,
                                level_type: LevelType,
                                content_type: ContentType,
                                context: str = "") -> bool:
        """
        Generate voice with automatic voice selection based on context.
        
        Args:
            text: Text to convert to speech
            filename: Output filename (without extension)
            level_type: The type of game level
            content_type: The type of content being spoken
            context: Additional context information
            
        Returns:
            bool: True if successful, False otherwise
        """
        
        # Get appropriate voice for this context
        voice_key, voice_config = self.assignment_system.get_voice_for_content(
            level_type, content_type, text, context
        )
        
        voice_id = voice_config.get("id")
        voice_settings = voice_config.get("settings", {})
        voice_name = voice_config.get("name", voice_key)
        
        self.logger.info(f"Selected voice '{voice_name}' for {content_type.value} in {level_type.value}")
        
        return self._generate_with_voice(text, filename, voice_id, voice_settings, voice_name)
    
    def _generate_with_voice(self, 
                           text: str, 
                           filename: str, 
                           voice_id: str, 
                           settings: Dict,
                           voice_name: str) -> bool:
        """Generate voice with specific voice ID and settings."""
        
        if not self.api_key:
            self.logger.error("No ElevenLabs API key available")
            return False
        
        output_path = os.path.join(self.sounds_dir, f"{filename}.wav")
        
        # Check if file already exists (caching)
        if os.path.exists(output_path):
            self.logger.info(f"Using cached voice file: {filename}.wav")
            return True
        
        # Prepare API request
        url = f"{self.base_url}/text-to-speech/{voice_id}"
        
        # Use settings from voice config
        voice_settings = {
            "stability": settings.get("stability", 0.75),
            "similarity_boost": settings.get("similarity_boost", 0.75),
            "style": settings.get("style", 0.0),
            "use_speaker_boost": settings.get("use_speaker_boost", True)
        }
        
        payload = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": voice_settings
        }
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        
        try:
            self.logger.info(f"Generating '{text}' with {voice_name}")
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Save the audio file
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            self.logger.info(f"Successfully generated voice: {filename}.wav with {voice_name}")
            return True
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"ElevenLabs API error for {filename}: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error generating {filename}: {e}")
            return False
    
    # Convenience methods for common game scenarios
    
    def generate_letter_voice(self, letter: str, level_type: LevelType) -> bool:
        """Generate voice for a letter in alphabet or case levels."""
        return self.generate_contextual_voice(
            letter, letter.lower(), level_type, ContentType.LETTER
        )
    
    def generate_emoji_voice(self, emoji_name: str, level_type: LevelType) -> bool:
        """Generate voice for emoji pronunciation in alphabet or case levels."""
        return self.generate_contextual_voice(
            emoji_name, f"emoji_{emoji_name.lower()}", level_type, ContentType.EMOJI, "emoji"
        )
    
    def generate_target_hit_voice(self, target_name: str, level_type: LevelType) -> bool:
        """Generate voice for target hit feedback in colors or shapes levels."""
        return self.generate_contextual_voice(
            target_name, target_name.lower(), level_type, ContentType.TARGET_HIT, "target_destroyed"
        )
    
    def generate_number_voice(self, number: str) -> bool:
        """Generate voice for numbers in numbers level."""
        return self.generate_contextual_voice(
            number, number, LevelType.NUMBERS, ContentType.NUMBER
        )
    
    def generate_general_voice(self, text: str, filename: str, level_type: LevelType = None) -> bool:
        """Generate voice for general game content."""
        if level_type is None:
            level_type = LevelType.ALPHABET  # Default level type
        
        return self.generate_contextual_voice(
            text, filename, level_type, ContentType.GENERAL
        )
    
    def test_contextual_generation(self):
        """Test the contextual voice generation system."""
        print("🎤 Testing Contextual Voice Generation")
        print("=" * 50)
        
        test_cases = [
            ("Letter A in Alphabet", lambda: self.generate_letter_voice("A", LevelType.ALPHABET)),
            ("Emoji 'apple' in Alphabet", lambda: self.generate_emoji_voice("apple", LevelType.ALPHABET)),
            ("Letter a in Case", lambda: self.generate_letter_voice("a", LevelType.CL_CASE)),
            ("Emoji 'ant' in Case", lambda: self.generate_emoji_voice("ant", LevelType.CL_CASE)),
            ("Color 'red' hit", lambda: self.generate_target_hit_voice("red", LevelType.COLORS)),
            ("Shape 'circle' hit", lambda: self.generate_target_hit_voice("circle", LevelType.SHAPES)),
            ("Number '5'", lambda: self.generate_number_voice("5")),
        ]
        
        for description, test_func in test_cases:
            try:
                result = test_func()
                status = "✅" if result else "❌"
                print(f"{status} {description}")
            except Exception as e:
                print(f"❌ {description} - Error: {e}")
        
        print("\n✅ Contextual voice generation test complete!")

def main():
    """Test the contextual voice generation system."""
    cvg = ContextAwareVoiceGenerator()
    cvg.test_contextual_generation()

if __name__ == "__main__":
    main()