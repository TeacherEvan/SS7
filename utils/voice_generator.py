"""
Voice generation utility for SS6 Super Student Game.
Generates realistic voice recordings using ElevenLabs API or Windows TTS fallback.
"""

import os
import json
import requests
import pygame
from typing import Dict, List, Optional
import logging

# Import Windows TTS fallback
try:
    from .windows_tts import WindowsTTSGenerator
    WINDOWS_TTS_AVAILABLE = True
except ImportError:
    try:
        from utils.windows_tts import WindowsTTSGenerator
        WINDOWS_TTS_AVAILABLE = True
    except ImportError:
        WINDOWS_TTS_AVAILABLE = False

class ElevenLabsVoiceGenerator:
    """
    Handles ElevenLabs API integration for generating realistic voice recordings.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the ElevenLabs voice generator.
        
        Args:
            api_key: ElevenLabs API key. If None, will try to read from environment or config.
        """
        self.api_key = api_key or self._get_api_key()
        self.base_url = "https://api.elevenlabs.io/v1"
        
        # Load voice configuration
        self.config = self._load_voice_config()
        self.voice_id = self.config.get('voice_id', "21m00Tcm4TlvDq8ikWAM")
        
        self.sounds_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sounds")
        self.voice_cache_dir = os.path.join(self.sounds_dir, "voice_cache")
        
        # Ensure directories exist
        os.makedirs(self.sounds_dir, exist_ok=True)
        os.makedirs(self.voice_cache_dir, exist_ok=True)
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def _get_api_key(self) -> Optional[str]:
        """Get API key from environment variable or config file."""
        # Try environment variable first
        api_key = os.environ.get('ELEVENLABS_API_KEY')
        if api_key:
            return api_key
            
        # Try config file
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "voice_config.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    return config.get('elevenlabs_api_key')
            except Exception as e:
                self.logger.warning(f"Could not read voice config: {e}")
                
        return None
    
    def _load_voice_config(self) -> Dict:
        """Load voice configuration from config file."""
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "voice_config.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    return config
            except Exception as e:
                self.logger.warning(f"Could not read voice config: {e}")
        
        # Return default config if loading fails
        return {
            "voice_id": "21m00Tcm4TlvDq8ikWAM",
            "voice_settings": {
                "stability": 0.75,
                "similarity_boost": 0.75
            }
        }
    
    def generate_voice(self, text: str, filename: str, stability: float = 0.75, 
                      similarity_boost: float = 0.75) -> bool:
        """
        Generate voice audio using ElevenLabs API.
        
        Args:
            text: Text to convert to speech
            filename: Output filename (without extension)
            stability: Voice stability (0.0-1.0)
            similarity_boost: Voice similarity boost (0.0-1.0)
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.api_key:
            self.logger.error("No ElevenLabs API key available")
            return False
            
        output_path = os.path.join(self.sounds_dir, f"{filename}.wav")
        cache_path = os.path.join(self.voice_cache_dir, f"{filename}.wav")
        
        # Check if already cached
        if os.path.exists(cache_path):
            self.logger.info(f"Using cached voice for {filename}")
            try:
                # Copy from cache to sounds directory
                import shutil
                shutil.copy2(cache_path, output_path)
                return True
            except Exception as e:
                self.logger.error(f"Error copying cached file: {e}")
        
        # Generate new voice
        url = f"{self.base_url}/text-to-speech/{self.voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": stability,
                "similarity_boost": similarity_boost
            }
        }
        
        try:
            self.logger.info(f"Generating voice for: {text}")
            response = requests.post(url, json=data, headers=headers, timeout=30)
            
            if response.status_code == 200:
                # Save to both cache and sounds directory
                with open(cache_path, 'wb') as f:
                    f.write(response.content)
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                    
                self.logger.info(f"Successfully generated voice for {filename}")
                return True
            else:
                self.logger.error(f"ElevenLabs API error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error generating voice for {filename}: {e}")
            return False
    
    def generate_all_game_voices(self) -> Dict[str, bool]:
        """
        Generate all voice files needed for the game.
        
        Returns:
            Dict mapping filename to success status
        """
        results = {}
        
        # Define all the content that needs voice generation
        voice_content = {
            # Alphabet
            'a': 'A', 'b': 'B', 'c': 'C', 'd': 'D', 'e': 'E', 'f': 'F', 'g': 'G',
            'h': 'H', 'I': 'I', 'J': 'J', 'K': 'K', 'L': 'L', 'M': 'M', 'N': 'N',
            'O': 'O', 'P': 'P', 'Q': 'Q', 'R': 'R', 'S': 'S', 'T': 'T', 'U': 'U',
            'V': 'V', 'W': 'W', 'X': 'X', 'Y': 'Y', 'Z': 'Z',
            
            # Numbers
            '1': 'One', '2': 'Two', '3': 'Three', '4': 'Four', '5': 'Five',
            '6': 'Six', '7': 'Seven', '8': 'Eight', '9': 'Nine', '10': 'Ten',
            
            # Colors
            'red': 'Red', 'blue': 'Blue', 'green': 'Green', 'yellow': 'Yellow',
            'purple': 'Purple',
            
            # Shapes
            'circle': 'Circle', 'square': 'Square', 'triangle': 'Triangle',
            'rectangle': 'Rectangle', 'pentagon': 'Pentagon',
            
            # Game sounds
            'explosion': 'Boom!', 'laser': 'Zap!',
            'correct': 'Well done!', 'incorrect': 'Try again!',
            'level_complete': 'Level complete! Excellent work!',
            'game_start': 'Welcome to Super Student! Let\'s learn together!',
        }
        
        total_items = len(voice_content)
        completed = 0
        
        for filename, text in voice_content.items():
            self.logger.info(f"Processing {completed + 1}/{total_items}: {filename}")
            success = self.generate_voice(text, filename)
            results[filename] = success
            completed += 1
            
            if success:
                self.logger.info(f"✓ Generated {filename}.wav")
            else:
                self.logger.error(f"✗ Failed to generate {filename}.wav")
        
        # Summary
        successful = sum(1 for success in results.values() if success)
        self.logger.info(f"Voice generation complete: {successful}/{total_items} successful")
        
        return results
    
    def test_voice_generation(self) -> bool:
        """
        Test the voice generation with a simple example.
        
        Returns:
            bool: True if test successful
        """
        return self.generate_voice("Hello, this is a test.", "voice_test")
    
    def get_available_voices(self) -> List[Dict]:
        """
        Get list of available voices from ElevenLabs.
        
        Returns:
            List of voice information dictionaries
        """
        if not self.api_key:
            return []
            
        url = f"{self.base_url}/voices"
        headers = {"xi-api-key": self.api_key}
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                return response.json().get('voices', [])
        except Exception as e:
            self.logger.error(f"Error fetching voices: {e}")
            
        return []


class VoiceManager:
    """
    Manages voice playback and fallback to synthesized sounds.
    """
    
    def __init__(self, sounds_dir: str):
        """
        Initialize the voice manager.
        
        Args:
            sounds_dir: Directory containing sound files
        """
        self.sounds_dir = sounds_dir
        self.sound_cache = {}
        self.voice_enabled = True
        
    def load_sound(self, filename: str) -> Optional[pygame.mixer.Sound]:
        """
        Load a sound file with caching.
        
        Args:
            filename: Sound filename (without extension)
            
        Returns:
            pygame.mixer.Sound object or None if not found
        """
        if filename in self.sound_cache:
            return self.sound_cache[filename]
            
        # Try to load the sound file
        sound_path = os.path.join(self.sounds_dir, f"{filename}.wav")
        
        if os.path.exists(sound_path):
            try:
                sound = pygame.mixer.Sound(sound_path)
                self.sound_cache[filename] = sound
                return sound
            except Exception as e:
                logging.error(f"Error loading sound {filename}: {e}")
                
        return None
    
    def play_sound(self, filename: str, volume: float = 1.0) -> bool:
        """
        Play a sound file.
        
        Args:
            filename: Sound filename (without extension)
            volume: Volume level (0.0-1.0)
            
        Returns:
            bool: True if sound played successfully
        """
        if not self.voice_enabled:
            return False
            
        sound = self.load_sound(filename)
        if sound:
            try:
                sound.set_volume(volume)
                sound.play()
                return True
            except Exception as e:
                logging.error(f"Error playing sound {filename}: {e}")
                
        return False
    
    def set_voice_enabled(self, enabled: bool):
        """Enable or disable voice playback."""
        self.voice_enabled = enabled
    
    def preload_common_sounds(self):
        """Preload commonly used sounds for better performance."""
        common_sounds = [
            'a', 'b', 'c', '1', '2', '3', 'red', 'blue', 'circle', 'square',
            'explosion', 'laser', 'correct', 'incorrect'
        ]
        
        for sound in common_sounds:
            self.load_sound(sound)


class UniversalVoiceGenerator:
    """
    Universal voice generator that tries ElevenLabs first, then falls back to Windows TTS.
    """
    
    def __init__(self):
        """Initialize the universal voice generator."""
        self.sounds_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sounds")
        self.logger = logging.getLogger(__name__)
        
        # Initialize generators
        self.elevenlabs_generator = ElevenLabsVoiceGenerator()
        self.windows_tts_generator = None
        
        self.logger.info(f"WINDOWS_TTS_AVAILABLE: {WINDOWS_TTS_AVAILABLE}")
        
        if WINDOWS_TTS_AVAILABLE:
            try:
                self.windows_tts_generator = WindowsTTSGenerator(self.sounds_dir)
                self.logger.info("WindowsTTSGenerator created successfully")
            except Exception as e:
                self.logger.error(f"Error creating WindowsTTSGenerator: {e}")
        
        # Check which generators are available
        self.elevenlabs_available = bool(self.elevenlabs_generator.api_key)
        self.windows_tts_available = (
            self.windows_tts_generator and 
            self.windows_tts_generator.is_available()
        )
        
        self.logger.info(f"Voice generators available:")
        self.logger.info(f"  ElevenLabs: {'✓' if self.elevenlabs_available else '✗'}")
        self.logger.info(f"  Windows TTS: {'✓' if self.windows_tts_available else '✗'}")
    
    def generate_voice_file(self, text: str, filename: str) -> bool:
        """
        Generate a voice file using the best available method.
        
        Args:
            text: Text to convert to speech
            filename: Output filename (without extension)
            
        Returns:
            bool: True if successful
        """
        # Try ElevenLabs first (highest quality)
        if self.elevenlabs_available:
            self.logger.info(f"Trying ElevenLabs for: {filename}")
            if self.elevenlabs_generator.generate_voice(text, filename):
                return True
            else:
                self.logger.warning(f"ElevenLabs failed for {filename}, trying Windows TTS")
        
        # Fall back to Windows TTS
        if self.windows_tts_available:
            self.logger.info(f"Using Windows TTS for: {filename}")
            return self.windows_tts_generator.generate_voice_wav(text, filename)
        
        # No voice generation available
        self.logger.error(f"No voice generation available for: {filename}")
        return False
    
    def generate_all_game_voices(self) -> Dict[str, bool]:
        """Generate all voice files needed for the game."""
        if self.windows_tts_available:
            # Use Windows TTS for all files - it's more reliable and faster
            self.logger.info("Using Windows TTS to generate all game voices")
            return self.windows_tts_generator.generate_all_game_voices()
        elif self.elevenlabs_available:
            # Fall back to ElevenLabs
            self.logger.info("Using ElevenLabs to generate all game voices")
            return self.elevenlabs_generator.generate_all_game_voices()
        else:
            self.logger.error("No voice generation methods available")
            return {}
    
    def is_available(self) -> bool:
        """Check if any voice generation method is available."""
        return self.elevenlabs_available or self.windows_tts_available


def setup_voice_config():
    """
    Setup voice configuration file for API key.
    """
    config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config")
    os.makedirs(config_dir, exist_ok=True)
    
    config_path = os.path.join(config_dir, "voice_config.json")
    
    if not os.path.exists(config_path):
        config = {
            "elevenlabs_api_key": "",
            "voice_id": "21m00Tcm4TlvDq8ikWAM",
            "voice_settings": {
                "stability": 0.75,
                "similarity_boost": 0.75
            },
            "enabled": True,
            "fallback_to_windows_tts": True
        }
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
            
        print(f"Created voice config file at: {config_path}")
        print("Windows TTS will be used as fallback voice generation.")
        
    return config_path


if __name__ == "__main__":
    # Setup and test voice generation
    setup_voice_config()
    
    # Use the universal generator
    generator = UniversalVoiceGenerator()
    
    if generator.is_available():
        print("Voice generation system available!")
        
        # Generate all game voices
        results = generator.generate_all_game_voices()
        
        successful = sum(1 for success in results.values() if success)
        total = len(results)
        
        print(f"\nVoice generation complete: {successful}/{total} files generated successfully")
        
        if successful < total:
            print("\nFailed files:")
            for filename, success in results.items():
                if not success:
                    print(f"  - {filename}")
    else:
        print("No voice generation methods available. Please install Windows TTS or add ElevenLabs API key.")