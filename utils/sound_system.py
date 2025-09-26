#!/usr/bin/env python3
"""
Sound System Module for SS6 Super Student Game
Provides the missing SoundSystem class referenced in tests and integrates with existing sound architecture.
"""

import logging
import os
from pathlib import Path
from typing import Dict, List, Optional

import pygame

from utils.voice_generator import VoiceManager


class SoundSystem:
    """
    Main sound system class that integrates with the existing SS6 architecture.
    Provides a unified interface for all game audio.
    """

    def __init__(self, sounds_dir: str = "sounds"):
        """
        Initialize the sound system.

        Args:
            sounds_dir: Directory containing sound files
        """
        self.sounds_dir = Path(sounds_dir)
        self.logger = logging.getLogger(__name__)

        # Initialize pygame mixer if not already done
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=1024)
                pygame.mixer.init()
                self.logger.info("Pygame mixer initialized")
            except pygame.error as e:
                self.logger.error(f"Failed to initialize pygame mixer: {e}")

        # Sound cache for performance
        self.sound_cache: Dict[str, pygame.mixer.Sound] = {}

        # Voice manager integration
        self.voice_manager = None
        try:
            self.voice_manager = VoiceManager(str(self.sounds_dir))
            self.logger.info("Voice manager initialized")
        except Exception as e:
            self.logger.warning(f"Voice manager initialization failed: {e}")

        # Audio settings
        self.master_volume = 1.0
        self.voice_volume = 0.8
        self.effects_volume = 1.0
        self.enabled = True

        # Preload common sounds
        self._preload_essential_sounds()

    def _preload_essential_sounds(self):
        """Preload commonly used sounds for better performance."""
        essential_sounds = [
            "explosion",
            "laser",  # Effects
            "a",
            "b",
            "c",
            "1",
            "2",
            "3",  # Common educational sounds
            "red",
            "blue",
            "circle",
            "square",  # Common game elements
        ]

        for sound_name in essential_sounds:
            self.load_sound(sound_name)

    def load_sound(self, sound_name: str) -> Optional[pygame.mixer.Sound]:
        """
        Load a sound file with caching.

        Args:
            sound_name: Name of the sound file (without extension)

        Returns:
            pygame.mixer.Sound object or None if not found
        """
        if sound_name in self.sound_cache:
            return self.sound_cache[sound_name]

        sound_path = self.sounds_dir / f"{sound_name}.wav"

        if sound_path.exists():
            try:
                sound = pygame.mixer.Sound(str(sound_path))
                self.sound_cache[sound_name] = sound
                return sound
            except pygame.error as e:
                self.logger.error(f"Failed to load sound {sound_name}: {e}")
        else:
            self.logger.warning(f"Sound file not found: {sound_path}")

        return None

    def play_voice(self, target: str, volume: Optional[float] = None) -> bool:
        """
        Play a voice sound for educational targets (letters, numbers, etc.).

        Args:
            target: The target to pronounce (letter, number, color, shape)
            volume: Volume override (0.0-1.0)

        Returns:
            bool: True if sound played successfully
        """
        if not self.enabled:
            return False

        # Use voice manager if available
        if self.voice_manager:
            return self.voice_manager.play_sound(target, volume or self.voice_volume)

        # Fallback to direct sound loading
        sound = self.load_sound(target)
        if sound:
            try:
                sound.set_volume((volume or self.voice_volume) * self.master_volume)
                sound.play()
                self.logger.debug(f"Played voice sound: {target}")
                return True
            except pygame.error as e:
                self.logger.error(f"Failed to play voice sound {target}: {e}")

        return False

    def play_effect(self, effect_name: str, volume: Optional[float] = None) -> bool:
        """
        Play a sound effect.

        Args:
            effect_name: Name of the effect sound
            volume: Volume override (0.0-1.0)

        Returns:
            bool: True if sound played successfully
        """
        if not self.enabled:
            return False

        sound = self.load_sound(effect_name)
        if sound:
            try:
                sound.set_volume((volume or self.effects_volume) * self.master_volume)
                sound.play()
                self.logger.debug(f"Played effect sound: {effect_name}")
                return True
            except pygame.error as e:
                self.logger.error(f"Failed to play effect sound {effect_name}: {e}")

        return False

    def set_master_volume(self, volume: float):
        """Set master volume for all sounds."""
        self.master_volume = max(0.0, min(1.0, volume))
        self.logger.info(f"Master volume set to: {self.master_volume}")

    def set_voice_volume(self, volume: float):
        """Set volume for voice sounds."""
        self.voice_volume = max(0.0, min(1.0, volume))
        self.logger.info(f"Voice volume set to: {self.voice_volume}")

    def set_effects_volume(self, volume: float):
        """Set volume for effect sounds."""
        self.effects_volume = max(0.0, min(1.0, volume))
        self.logger.info(f"Effects volume set to: {self.effects_volume}")

    def enable_sound(self, enabled: bool = True):
        """Enable or disable all sound playback."""
        self.enabled = enabled
        self.logger.info(f"Sound system {'enabled' if enabled else 'disabled'}")

    def get_available_sounds(self) -> List[str]:
        """Get list of available sound files."""
        if not self.sounds_dir.exists():
            return []

        return [f.stem for f in self.sounds_dir.glob("*.wav")]

    def get_sound_info(self) -> Dict:
        """Get information about the sound system."""
        available_sounds = self.get_available_sounds()

        return {
            "sounds_directory": str(self.sounds_dir),
            "total_sounds": len(available_sounds),
            "cached_sounds": len(self.sound_cache),
            "pygame_mixer_init": pygame.mixer.get_init() is not None,
            "voice_manager_available": self.voice_manager is not None,
            "master_volume": self.master_volume,
            "voice_volume": self.voice_volume,
            "effects_volume": self.effects_volume,
            "enabled": self.enabled,
        }

    def validate_educational_sounds(self) -> Dict:
        """Validate that essential educational sounds are available."""
        validation_results = {
            "missing_sounds": [],
            "available_sounds": [],
            "categories": {
                "letters": {"expected": [], "found": []},
                "numbers": {"expected": [], "found": []},
                "colors": {"expected": [], "found": []},
                "shapes": {"expected": [], "found": []},
            },
        }

        # Define expected educational sounds
        expected_categories = {
            "letters": [chr(65 + i) for i in range(26)]
            + [chr(97 + i) for i in range(26)],  # A-Z, a-z
            "numbers": [str(i) for i in range(1, 11)],  # 1-10
            "colors": ["red", "blue", "green", "yellow", "purple"],
            "shapes": ["circle", "square", "triangle", "rectangle", "pentagon"],
        }

        available_sounds = self.get_available_sounds()

        # Check each category
        for category, expected in expected_categories.items():
            validation_results["categories"][category]["expected"] = expected

            for sound_name in expected:
                if sound_name in available_sounds:
                    validation_results["categories"][category]["found"].append(sound_name)
                    validation_results["available_sounds"].append(sound_name)
                else:
                    validation_results["missing_sounds"].append(sound_name)

        return validation_results

    def cleanup(self):
        """Clean up sound system resources."""
        self.sound_cache.clear()
        if self.voice_manager:
            # Voice manager cleanup if it has such method
            pass
        self.logger.info("Sound system cleaned up")


# Global sound system instance for easy access
_sound_system_instance = None


def get_sound_system() -> SoundSystem:
    """Get the global sound system instance."""
    global _sound_system_instance
    if _sound_system_instance is None:
        _sound_system_instance = SoundSystem()
    return _sound_system_instance


def cleanup_sound_system():
    """Clean up the global sound system instance."""
    global _sound_system_instance
    if _sound_system_instance:
        _sound_system_instance.cleanup()
        _sound_system_instance = None
