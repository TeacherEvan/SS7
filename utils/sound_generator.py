#!/usr/bin/env python3
"""
Sound Generator for SS6 Super Student Game
Creates basic sound effects programmatically using numpy and pygame.
Enhanced with AI voice integration and fallback systems.
"""

import logging
import os
from typing import Optional

import numpy as np
import pygame

# Import the new voice and music systems
try:
    from .music_manager import BackgroundMusicManager, LevelMusicIntegrator, MusicTheme
    from .voice_generator import ElevenLabsVoiceGenerator, VoiceManager

    VOICE_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Voice/Music systems not available: {e}")
    VOICE_AVAILABLE = False


def generate_explosion_sound(duration=0.3, sample_rate=44100):
    """Generate a explosion sound effect."""
    frames = int(duration * sample_rate)

    # Create explosion sound using noise and envelope
    # White noise for the base
    noise = np.random.uniform(-1, 1, frames)

    # Add some low frequency rumble
    t = np.linspace(0, duration, frames)
    rumble = 0.3 * np.sin(2 * np.pi * 60 * t) + 0.2 * np.sin(2 * np.pi * 120 * t)

    # Combine noise and rumble
    sound = 0.7 * noise + 0.3 * rumble

    # Apply exponential decay envelope
    envelope = np.exp(-5 * t)
    sound = sound * envelope

    # Normalize and convert to 16-bit integers
    sound = np.clip(sound, -1, 1)
    sound = (sound * 32767).astype(np.int16)

    return sound


def generate_laser_sound(duration=0.2, sample_rate=44100):
    """Generate a laser/zap sound effect."""
    frames = int(duration * sample_rate)
    t = np.linspace(0, duration, frames)

    # Frequency sweep from high to low
    freq_start = 800
    freq_end = 200
    freq = freq_start * np.exp(-3 * t) + freq_end

    # Create the main laser tone
    laser = np.sin(2 * np.pi * freq * t)

    # Add some harmonics for richness
    laser += 0.3 * np.sin(2 * np.pi * 2 * freq * t)
    laser += 0.1 * np.sin(2 * np.pi * 3 * freq * t)

    # Apply envelope
    envelope = np.exp(-8 * t)
    laser = laser * envelope

    # Normalize and convert to 16-bit integers
    laser = np.clip(laser, -1, 1)
    laser = (laser * 32767).astype(np.int16)

    return laser


def generate_beep_sound(note_name, duration=0.15, sample_rate=44100):
    """Generate a simple beep sound for letter/number announcements."""
    # Note frequencies (simplified)
    notes = {
        "C4": 261.63,
        "D4": 293.66,
        "E4": 329.63,
        "F4": 349.23,
        "G4": 392.00,
        "A4": 440.00,
        "B4": 493.88,
        "C5": 523.25,
    }

    freq = notes.get(note_name, 440.0)  # Default to A4
    frames = int(duration * sample_rate)
    t = np.linspace(0, duration, frames)

    # Simple sine wave
    beep = np.sin(2 * np.pi * freq * t)

    # Apply envelope to avoid clicks
    envelope = np.exp(-3 * t)
    beep = beep * envelope

    # Normalize and convert to 16-bit integers
    beep = np.clip(beep, -1, 1)
    beep = (beep * 32767).astype(np.int16)

    return beep


def save_wav_file(filename, audio_data, sample_rate=44100):
    """Save audio data as a WAV file using basic WAV format."""
    import struct

    # Ensure stereo format
    if len(audio_data.shape) == 1:
        audio_data = np.column_stack((audio_data, audio_data))

    # WAV file header
    with open(filename, "wb") as wav_file:
        # RIFF header
        wav_file.write(b"RIFF")
        wav_file.write(struct.pack("<I", 36 + len(audio_data) * 4))  # File size
        wav_file.write(b"WAVE")

        # Format chunk
        wav_file.write(b"fmt ")
        wav_file.write(struct.pack("<I", 16))  # Chunk size
        wav_file.write(struct.pack("<H", 1))  # Audio format (PCM)
        wav_file.write(struct.pack("<H", 2))  # Number of channels (stereo)
        wav_file.write(struct.pack("<I", sample_rate))  # Sample rate
        wav_file.write(struct.pack("<I", sample_rate * 4))  # Byte rate
        wav_file.write(struct.pack("<H", 4))  # Block align
        wav_file.write(struct.pack("<H", 16))  # Bits per sample

        # Data chunk
        wav_file.write(b"data")
        wav_file.write(struct.pack("<I", len(audio_data) * 4))  # Data size

        # Write audio data
        for frame in audio_data:
            wav_file.write(struct.pack("<hh", int(frame[0]), int(frame[1])))


def generate_voice_beep(pitch_hz=440, duration=0.6, sample_rate=44100):
    """Generate a voice-like beep with formants for speech simulation."""
    frames = int(duration * sample_rate)
    t = np.linspace(0, duration, frames)

    # Create fundamental frequency
    fundamental = 0.4 * np.sin(2 * np.pi * pitch_hz * t)

    # Add formant frequencies (vowel-like characteristics)
    formant1 = 0.2 * np.sin(2 * np.pi * (pitch_hz * 2.2) * t)  # First formant
    formant2 = 0.1 * np.sin(2 * np.pi * (pitch_hz * 3.5) * t)  # Second formant

    # Combine fundamental and formants
    sound = fundamental + formant1 + formant2

    # Add slight vibrato for more natural feel
    vibrato = 1 + 0.05 * np.sin(2 * np.pi * 6 * t)
    sound *= vibrato

    # Apply envelope to avoid clicks
    envelope = np.ones(frames)
    fade_frames = int(0.1 * sample_rate)  # 100ms fade in/out
    envelope[:fade_frames] = np.linspace(0, 1, fade_frames)
    envelope[-fade_frames:] = np.linspace(1, 0, fade_frames)
    sound *= envelope

    # Normalize and convert to 16-bit
    sound = np.clip(sound, -1, 1)
    sound = (sound * 32767).astype(np.int16)

    return sound


def generate_all_voice_sounds(sounds_dir):
    """Generate voice sounds for all game targets with distinct pitches."""
    print("🗣️ Generating voice sounds for all targets...")

    # Define pitch mappings for different categories
    # Letters: Middle range pitches
    letter_base_pitch = 200
    letter_pitch_increment = 12

    # Numbers: Lower pitches
    number_base_pitch = 150
    number_pitch_increment = 18

    # Colors: Higher pitches with distinct tones
    color_pitches = {"blue": 280, "red": 320, "green": 260, "yellow": 340, "purple": 380}

    # Shapes: Mid-high pitches with longer duration
    shape_pitches = {
        "circle": 240,
        "square": 270,
        "triangle": 300,
        "rectangle": 330,
        "pentagon": 360,
    }

    sound_count = 0

    # Generate uppercase letters (A-Z)
    for i, letter in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
        pitch = letter_base_pitch + (i * letter_pitch_increment)
        sound = generate_voice_beep(pitch, duration=0.7)
        sound_stereo = np.column_stack((sound, sound))
        save_wav_file(os.path.join(sounds_dir, f"{letter}.wav"), sound_stereo)
        sound_count += 1

    # Generate lowercase letters (a-z) - slightly lower pitch
    for i, letter in enumerate("abcdefghijklmnopqrstuvwxyz"):
        pitch = letter_base_pitch + (i * letter_pitch_increment) - 40  # Lower for lowercase
        sound = generate_voice_beep(pitch, duration=0.7)
        sound_stereo = np.column_stack((sound, sound))
        save_wav_file(os.path.join(sounds_dir, f"{letter}.wav"), sound_stereo)
        sound_count += 1

    # Generate numbers (1-10)
    for i in range(1, 11):
        pitch = number_base_pitch + (i * number_pitch_increment)
        sound = generate_voice_beep(pitch, duration=0.8)
        sound_stereo = np.column_stack((sound, sound))
        save_wav_file(os.path.join(sounds_dir, f"{i}.wav"), sound_stereo)
        sound_count += 1

    # Generate colors
    for color, pitch in color_pitches.items():
        sound = generate_voice_beep(pitch, duration=0.9)
        sound_stereo = np.column_stack((sound, sound))
        save_wav_file(os.path.join(sounds_dir, f"{color}.wav"), sound_stereo)
        sound_count += 1

    # Generate shapes (lowercase for consistency with game)
    for shape, pitch in shape_pitches.items():
        sound = generate_voice_beep(pitch, duration=1.0)
        sound_stereo = np.column_stack((sound, sound))
        save_wav_file(os.path.join(sounds_dir, f"{shape.lower()}.wav"), sound_stereo)
        sound_count += 1

    print(f"✅ Created {sound_count} voice sound files:")
    print(f"   - 26 uppercase letters (A-Z)")
    print(f"   - 26 lowercase letters (a-z)")
    print(f"   - 10 numbers (1-10)")
    print(f"   - 5 colors (blue, red, green, yellow, purple)")
    print(f"   - 5 shapes (circle, square, triangle, rectangle, pentagon)")


def create_sound_files(sounds_dir):
    """Create all basic sound files."""
    print("🎵 Generating sound effects...")

    try:
        import numpy as np
    except ImportError:
        print("❌ NumPy not available. Creating placeholder sound files...")
        # Create minimal placeholder files
        with open(os.path.join(sounds_dir, "explosion.wav"), "w") as f:
            f.write("")  # Empty placeholder
        with open(os.path.join(sounds_dir, "laser.wav"), "w") as f:
            f.write("")  # Empty placeholder
        return

    # Generate explosion sound
    explosion_data = generate_explosion_sound()
    explosion_stereo = np.column_stack((explosion_data, explosion_data))

    # Generate laser sound
    laser_data = generate_laser_sound()
    laser_stereo = np.column_stack((laser_data, laser_data))

    # Save to files
    explosion_path = os.path.join(sounds_dir, "explosion.wav")
    laser_path = os.path.join(sounds_dir, "laser.wav")

    save_wav_file(explosion_path, explosion_stereo)
    save_wav_file(laser_path, laser_stereo)

    print(f"✅ Created explosion.wav")
    print(f"✅ Created laser.wav")

    # Generate comprehensive voice sounds for all game targets
    generate_all_voice_sounds(sounds_dir)


class EnhancedSoundSystem:
    """
    Enhanced sound system that combines AI voices, background music, and fallback beeps.
    """

    def __init__(self, sounds_dir: str):
        """
        Initialize the enhanced sound system.

        Args:
            sounds_dir: Directory containing sound files
        """
        self.sounds_dir = sounds_dir
        self.logger = logging.getLogger(__name__)

        # Initialize components
        self.voice_manager = None
        self.music_manager = None
        self.music_integrator = None

        if VOICE_AVAILABLE:
            try:
                self.voice_manager = VoiceManager(sounds_dir)
                self.music_manager = BackgroundMusicManager()
                self.music_integrator = LevelMusicIntegrator(self.music_manager)
                self.logger.info("Enhanced sound system initialized with AI voice support")
            except Exception as e:
                self.logger.error(f"Error initializing enhanced sound system: {e}")
                VOICE_AVAILABLE = False

        if not VOICE_AVAILABLE:
            self.logger.info("Enhanced sound system initialized with fallback beeps only")

    def play_target_sound(self, target: str, volume: float = 1.0) -> bool:
        """
        Play sound for a game target (letter, number, color, shape).

        Args:
            target: The target to play sound for
            volume: Volume level (0.0-1.0)

        Returns:
            bool: True if sound played successfully
        """
        # Try AI voice first
        if self.voice_manager and self.voice_manager.play_sound(target, volume):
            return True

        # Fallback to synthesized beep
        return self._play_fallback_beep(target, volume)

    def _play_fallback_beep(self, target: str, volume: float = 1.0) -> bool:
        """Play fallback synthesized beep for a target."""
        try:
            # Load existing beep sound if available
            sound_path = os.path.join(self.sounds_dir, f"{target}.wav")
            if os.path.exists(sound_path):
                sound = pygame.mixer.Sound(sound_path)
                sound.set_volume(volume)
                sound.play()
                return True
        except Exception as e:
            self.logger.error(f"Error playing fallback sound for {target}: {e}")

        return False

    def play_effect_sound(self, effect: str, volume: float = 1.0) -> bool:
        """
        Play a sound effect (explosion, laser, etc.).

        Args:
            effect: Name of the effect
            volume: Volume level (0.0-1.0)

        Returns:
            bool: True if sound played successfully
        """
        # Try voice manager first for speech effects
        if self.voice_manager and effect in [
            "correct",
            "incorrect",
            "level_complete",
            "game_start",
        ]:
            return self.voice_manager.play_sound(effect, volume)

        # Try regular sound files
        try:
            sound_path = os.path.join(self.sounds_dir, f"{effect}.wav")
            if os.path.exists(sound_path):
                sound = pygame.mixer.Sound(sound_path)
                sound.set_volume(volume)
                sound.play()
                return True
        except Exception as e:
            self.logger.error(f"Error playing effect sound {effect}: {e}")

        return False

    def start_level_music(self, level_name: str):
        """Start background music for a level."""
        if self.music_integrator:
            self.music_integrator.start_level_music(level_name)

    def stop_level_music(self):
        """Stop level background music."""
        if self.music_integrator:
            self.music_integrator.stop_level_music()

    def play_menu_music(self):
        """Play menu music."""
        if self.music_integrator:
            self.music_integrator.play_menu_music()

    def play_victory_music(self):
        """Play victory music."""
        if self.music_integrator:
            self.music_integrator.play_victory_music()

    def set_music_volume(self, volume: float):
        """Set background music volume."""
        if self.music_manager:
            self.music_manager.set_volume(volume)

    def set_voice_enabled(self, enabled: bool):
        """Enable or disable voice playback."""
        if self.voice_manager:
            self.voice_manager.set_voice_enabled(enabled)

    def set_music_enabled(self, enabled: bool):
        """Enable or disable background music."""
        if self.music_manager:
            self.music_manager.set_music_enabled(enabled)

    def preload_sounds(self):
        """Preload common sounds for better performance."""
        if self.voice_manager:
            self.voice_manager.preload_common_sounds()

    def get_sound_info(self) -> dict:
        """Get information about the sound system."""
        info = {
            "voice_available": self.voice_manager is not None,
            "music_available": self.music_manager is not None,
            "sounds_directory": self.sounds_dir,
        }

        if self.voice_manager:
            info["voice_enabled"] = self.voice_manager.voice_enabled

        if self.music_manager:
            info.update(self.music_manager.get_current_info())
            info["music_enabled"] = self.music_manager.is_music_enabled()

        return info


def setup_enhanced_sound_system(sounds_dir: str) -> EnhancedSoundSystem:
    """
    Set up the enhanced sound system with AI voices and music.

    Args:
        sounds_dir: Directory containing sound files

    Returns:
        EnhancedSoundSystem instance
    """
    # Ensure sounds directory exists
    os.makedirs(sounds_dir, exist_ok=True)

    # Create enhanced sound system
    sound_system = EnhancedSoundSystem(sounds_dir)

    # Generate fallback sounds if they don't exist
    if not os.path.exists(os.path.join(sounds_dir, "explosion.wav")):
        create_sound_files(sounds_dir)

    # Preload common sounds
    sound_system.preload_sounds()

    return sound_system


if __name__ == "__main__":
    # Test the enhanced sound system
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up one level to the main SS6 directory
    ss6_dir = os.path.dirname(script_dir)
    sounds_dir = os.path.join(ss6_dir, "sounds")

    if not os.path.exists(sounds_dir):
        os.makedirs(sounds_dir)

    # Create fallback sound files
    create_sound_files(sounds_dir)

    # Test enhanced sound system
    enhanced_system = setup_enhanced_sound_system(sounds_dir)

    print("Enhanced Sound System Test:")
    print("=" * 40)

    info = enhanced_system.get_sound_info()
    for key, value in info.items():
        print(f"{key}: {value}")

    print("\nTesting sound playback...")
    enhanced_system.play_target_sound("a")
    enhanced_system.play_effect_sound("explosion")

    print("Enhanced sound system setup complete!")
