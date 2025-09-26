"""
Background music manager for SS6 Super Student Game.
Handles educational-themed background music for different levels.
"""

import json
import logging
import os
import random
from enum import Enum
from typing import Dict, List, Optional, Tuple

import pygame


class MusicTheme(Enum):
    """Educational music themes for different levels."""

    ALPHABET = "alphabet"
    NUMBERS = "numbers"
    COLORS = "colors"
    SHAPES = "shapes"
    GENERAL = "general"
    MENU = "menu"
    VICTORY = "victory"


class BackgroundMusicManager:
    """
    Manages background music playback with educational themes.
    """

    def __init__(self, music_dir: str = None):
        """
        Initialize the background music manager.

        Args:
            music_dir: Directory containing music files
        """
        self.music_dir = music_dir or os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "music"
        )
        self.config_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "config", "music_config.json"
        )

        # Ensure directories exist
        os.makedirs(self.music_dir, exist_ok=True)

        # Music state
        self.current_theme = None
        self.current_track = None
        self.is_playing = False
        self.volume = 0.3  # Background music should be subtle
        self.fade_duration = 2000  # 2 seconds fade

        # Load configuration
        self.config = self._load_config()

        # Music library organized by theme
        self.music_library = self._scan_music_library()

        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # Initialize pygame mixer if not already initialized
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

    def _load_config(self) -> Dict:
        """Load music configuration from file."""
        default_config = {
            "enabled": True,
            "volume": 0.3,
            "fade_duration": 2000,
            "shuffle_tracks": True,
            "themes": {
                "alphabet": {
                    "tracks": ["alphabet_song.mp3", "learning_letters.mp3"],
                    "volume": 0.25,
                },
                "numbers": {"tracks": ["counting_fun.mp3", "number_dance.mp3"], "volume": 0.25},
                "colors": {"tracks": ["rainbow_melody.mp3", "color_symphony.mp3"], "volume": 0.25},
                "shapes": {
                    "tracks": ["geometry_groove.mp3", "shape_adventure.mp3"],
                    "volume": 0.25,
                },
                "general": {
                    "tracks": ["happy_learning.mp3", "educational_ambient.mp3"],
                    "volume": 0.3,
                },
                "menu": {"tracks": ["welcome_theme.mp3", "menu_ambient.mp3"], "volume": 0.2},
                "victory": {"tracks": ["celebration.mp3", "success_fanfare.mp3"], "volume": 0.4},
            },
        }

        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r") as f:
                    config = json.load(f)
                    # Merge with defaults for any missing keys
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            except Exception as e:
                self.logger.error(f"Error loading music config: {e}")

        # Create default config file
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, "w") as f:
            json.dump(default_config, f, indent=2)

        return default_config

    def _scan_music_library(self) -> Dict[MusicTheme, List[str]]:
        """Scan the music directory and organize tracks by theme."""
        library = {theme: [] for theme in MusicTheme}

        if not os.path.exists(self.music_dir):
            return library

        # Scan for music files
        music_extensions = [".mp3", ".ogg", ".wav"]

        for filename in os.listdir(self.music_dir):
            if any(filename.lower().endswith(ext) for ext in music_extensions):
                file_path = os.path.join(self.music_dir, filename)

                # Categorize by filename patterns
                filename_lower = filename.lower()

                if any(word in filename_lower for word in ["alphabet", "letter", "abc"]):
                    library[MusicTheme.ALPHABET].append(file_path)
                elif any(word in filename_lower for word in ["number", "count", "math"]):
                    library[MusicTheme.NUMBERS].append(file_path)
                elif any(word in filename_lower for word in ["color", "rainbow", "paint"]):
                    library[MusicTheme.COLORS].append(file_path)
                elif any(
                    word in filename_lower for word in ["shape", "geometry", "circle", "square"]
                ):
                    library[MusicTheme.SHAPES].append(file_path)
                elif any(word in filename_lower for word in ["menu", "welcome", "title"]):
                    library[MusicTheme.MENU].append(file_path)
                elif any(
                    word in filename_lower for word in ["victory", "win", "success", "celebrate"]
                ):
                    library[MusicTheme.VICTORY].append(file_path)
                else:
                    library[MusicTheme.GENERAL].append(file_path)

        return library

    def play_theme(self, theme: MusicTheme, fade_in: bool = True) -> bool:
        """
        Play background music for a specific theme.

        Args:
            theme: Music theme to play
            fade_in: Whether to fade in the music

        Returns:
            bool: True if music started successfully
        """
        if not self.config.get("enabled", True):
            return False

        available_tracks = self.music_library.get(theme, [])

        if not available_tracks:
            # Fallback to general theme
            available_tracks = self.music_library.get(MusicTheme.GENERAL, [])
            if not available_tracks:
                self.logger.warning(f"No music available for theme {theme}")
                return False

        # Select track
        if self.config.get("shuffle_tracks", True):
            track_path = random.choice(available_tracks)
        else:
            track_path = available_tracks[0]

        try:
            # Stop current music if playing
            if self.is_playing:
                pygame.mixer.music.fadeout(self.fade_duration // 2)
                pygame.time.wait(self.fade_duration // 2)

            # Load and play new track
            pygame.mixer.music.load(track_path)

            # Set volume based on theme config
            theme_config = self.config.get("themes", {}).get(theme.value, {})
            volume = theme_config.get("volume", self.volume)
            pygame.mixer.music.set_volume(volume)

            # Play with or without fade
            if fade_in:
                pygame.mixer.music.play(loops=-1, fade_ms=self.fade_duration)
            else:
                pygame.mixer.music.play(loops=-1)

            self.current_theme = theme
            self.current_track = track_path
            self.is_playing = True

            self.logger.info(f"Started playing {theme.value} theme: {os.path.basename(track_path)}")
            return True

        except Exception as e:
            self.logger.error(f"Error playing music theme {theme}: {e}")
            return False

    def stop_music(self, fade_out: bool = True):
        """
        Stop background music.

        Args:
            fade_out: Whether to fade out the music
        """
        if self.is_playing:
            try:
                if fade_out:
                    pygame.mixer.music.fadeout(self.fade_duration)
                else:
                    pygame.mixer.music.stop()

                self.is_playing = False
                self.current_theme = None
                self.current_track = None

                self.logger.info("Stopped background music")

            except Exception as e:
                self.logger.error(f"Error stopping music: {e}")

    def pause_music(self):
        """Pause the current music."""
        if self.is_playing:
            try:
                pygame.mixer.music.pause()
                self.logger.info("Paused background music")
            except Exception as e:
                self.logger.error(f"Error pausing music: {e}")

    def resume_music(self):
        """Resume paused music."""
        try:
            pygame.mixer.music.unpause()
            self.logger.info("Resumed background music")
        except Exception as e:
            self.logger.error(f"Error resuming music: {e}")

    def set_volume(self, volume: float):
        """
        Set the music volume.

        Args:
            volume: Volume level (0.0-1.0)
        """
        self.volume = max(0.0, min(1.0, volume))

        if self.is_playing:
            try:
                pygame.mixer.music.set_volume(self.volume)
            except Exception as e:
                self.logger.error(f"Error setting volume: {e}")

    def next_track(self):
        """Skip to the next track in the current theme."""
        if self.current_theme and self.is_playing:
            self.play_theme(self.current_theme, fade_in=False)

    def get_current_info(self) -> Dict:
        """Get information about the currently playing music."""
        return {
            "theme": self.current_theme.value if self.current_theme else None,
            "track": os.path.basename(self.current_track) if self.current_track else None,
            "is_playing": self.is_playing,
            "volume": self.volume,
        }

    def is_music_enabled(self) -> bool:
        """Check if background music is enabled."""
        return self.config.get("enabled", True)

    def set_music_enabled(self, enabled: bool):
        """Enable or disable background music."""
        self.config["enabled"] = enabled

        if not enabled and self.is_playing:
            self.stop_music()

        # Save config
        try:
            with open(self.config_path, "w") as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving music config: {e}")

    def create_sample_music_files(self):
        """
        Create sample music file references for testing.
        This would normally be replaced with actual music files.
        """
        sample_tracks = {
            "alphabet_song.mp3": "Educational alphabet song with cheerful melody",
            "learning_letters.mp3": "Ambient music for letter learning activities",
            "counting_fun.mp3": "Upbeat counting song for number games",
            "number_dance.mp3": "Rhythmic music for math activities",
            "rainbow_melody.mp3": "Colorful melody for color recognition games",
            "color_symphony.mp3": "Orchestral piece with color themes",
            "geometry_groove.mp3": "Modern beats for shape learning",
            "shape_adventure.mp3": "Adventure theme for geometry games",
            "happy_learning.mp3": "General uplifting educational background music",
            "educational_ambient.mp3": "Calm ambient music for focused learning",
            "welcome_theme.mp3": "Welcoming melody for menu screens",
            "menu_ambient.mp3": "Soft background music for navigation",
            "celebration.mp3": "Victory celebration music",
            "success_fanfare.mp3": "Achievement fanfare for completed levels",
        }

        readme_path = os.path.join(self.music_dir, "README.md")
        with open(readme_path, "w") as f:
            f.write("# SS6 Background Music\n\n")
            f.write("This directory should contain educational background music files.\n\n")
            f.write("## Recommended Tracks:\n\n")

            for filename, description in sample_tracks.items():
                f.write(f"- **{filename}**: {description}\n")

            f.write("\n## File Format Support:\n")
            f.write("- MP3 (recommended for smaller file sizes)\n")
            f.write("- OGG (good compression, open source)\n")
            f.write("- WAV (uncompressed, larger files)\n")

            f.write("\n## Volume Guidelines:\n")
            f.write("- Background music should be subtle (0.2-0.4 volume)\n")
            f.write("- Avoid music with lyrics that might distract from learning\n")
            f.write("- Choose calm, positive melodies that enhance focus\n")


class LevelMusicIntegrator:
    """
    Integrates background music with the existing SS6 level system.
    """

    def __init__(self, music_manager: BackgroundMusicManager):
        """
        Initialize the level music integrator.

        Args:
            music_manager: Background music manager instance
        """
        self.music_manager = music_manager
        self.level_themes = {
            "alphabet_level": MusicTheme.ALPHABET,
            "numbers_level": MusicTheme.NUMBERS,
            "colors_level": MusicTheme.COLORS,
            "shapes_level": MusicTheme.SHAPES,
            "cl_case_level": MusicTheme.ALPHABET,  # Case sensitivity is alphabet-related
        }

    def start_level_music(self, level_name: str):
        """
        Start appropriate background music for a level.

        Args:
            level_name: Name of the level (e.g., "alphabet_level")
        """
        theme = self.level_themes.get(level_name, MusicTheme.GENERAL)
        self.music_manager.play_theme(theme)

    def stop_level_music(self):
        """Stop level background music."""
        self.music_manager.stop_music()

    def play_menu_music(self):
        """Play menu/welcome screen music."""
        self.music_manager.play_theme(MusicTheme.MENU)

    def play_victory_music(self):
        """Play victory/completion music."""
        self.music_manager.play_theme(MusicTheme.VICTORY)


if __name__ == "__main__":
    # Test the background music manager
    music_manager = BackgroundMusicManager()
    music_manager.create_sample_music_files()

    print("Background Music Manager initialized successfully!")
    print(f"Music directory: {music_manager.music_dir}")
    print(f"Configuration: {music_manager.config_path}")

    # Test integration
    integrator = LevelMusicIntegrator(music_manager)
    print("Level music integration ready!")
