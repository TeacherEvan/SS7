"""
Windows Text-to-Speech Voice Generator for SS6 Super Student Game.
Uses Windows built-in Speech API via PowerShell to generate actual speech.
"""

import logging
import os
import subprocess
import tempfile
import time
from typing import Dict, List, Optional

import pygame


class WindowsTTSGenerator:
    """
    Generates voice files using Windows built-in Text-to-Speech.
    """

    def __init__(self, sounds_dir: str):
        """
        Initialize the Windows TTS generator.

        Args:
            sounds_dir: Directory to save generated voice files
        """
        self.sounds_dir = sounds_dir
        self.logger = logging.getLogger(__name__)

        # Ensure sounds directory exists
        os.makedirs(sounds_dir, exist_ok=True)

        # Test if Windows TTS is available
        self.tts_available = self._test_tts_availability()

    def _test_tts_availability(self) -> bool:
        """Test if Windows TTS is available on this system."""
        try:
            # Try a simple TTS test
            test_cmd = [
                "powershell",
                "-Command",
                'Add-Type -AssemblyName System.Speech; $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; $synth.Speak("test"); $synth.Dispose()',
            ]
            result = subprocess.run(test_cmd, capture_output=True, timeout=10, text=True)
            success = result.returncode == 0

            if success:
                self.logger.info("Windows TTS is available")
            else:
                self.logger.warning(f"Windows TTS test failed: {result.stderr}")

            return success

        except Exception as e:
            self.logger.error(f"Error testing TTS availability: {e}")
            return False

    def generate_voice_wav(
        self, text: str, filename: str, rate: int = 0, volume: int = 100
    ) -> bool:
        """
        Generate a WAV file using Windows TTS.

        Args:
            text: Text to convert to speech
            filename: Output filename (without extension)
            rate: Speech rate (-10 to 10, 0 is normal)
            volume: Volume (0-100)

        Returns:
            bool: True if successful
        """
        if not self.tts_available:
            self.logger.warning("Windows TTS not available")
            return False

        output_path = os.path.join(self.sounds_dir, f"{filename}.wav")

        try:
            # PowerShell command to generate WAV file
            powershell_cmd = f"""
            Add-Type -AssemblyName System.Speech
            $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
            $synth.Rate = {rate}
            $synth.Volume = {volume}
            
            # Set output to WAV file
            $synth.SetOutputToWaveFile("{output_path}")
            $synth.Speak("{text}")
            $synth.Dispose()
            """

            # Execute PowerShell command
            result = subprocess.run(
                ["powershell", "-Command", powershell_cmd],
                capture_output=True,
                timeout=30,
                text=True,
            )

            if result.returncode == 0 and os.path.exists(output_path):
                self.logger.info(f"Generated voice file: {filename}.wav")
                return True
            else:
                self.logger.error(f"Failed to generate {filename}.wav: {result.stderr}")
                return False

        except Exception as e:
            self.logger.error(f"Error generating voice for {filename}: {e}")
            return False

    def generate_all_game_voices(self) -> Dict[str, bool]:
        """
        Generate voice files for all game targets.

        Returns:
            dict: Results of generation attempts
        """
        results = {}

        # Define the text to speak for each target
        voice_texts = {
            # Letters (uppercase)
            "A": "A",
            "B": "B",
            "C": "C",
            "D": "D",
            "E": "E",
            "F": "F",
            "G": "G",
            "H": "H",
            "I": "I",
            "J": "J",
            "K": "K",
            "L": "L",
            "M": "M",
            "N": "N",
            "O": "O",
            "P": "P",
            "Q": "Q",
            "R": "R",
            "S": "S",
            "T": "T",
            "U": "U",
            "V": "V",
            "W": "W",
            "X": "X",
            "Y": "Y",
            "Z": "Z",
            # Letters (lowercase)
            "a": "a",
            "b": "b",
            "c": "c",
            "d": "d",
            "e": "e",
            "f": "f",
            "g": "g",
            "h": "h",
            "i": "i",
            "j": "j",
            "k": "k",
            "l": "l",
            "m": "m",
            "n": "n",
            "o": "o",
            "p": "p",
            "q": "q",
            "r": "r",
            "s": "s",
            "t": "t",
            "u": "u",
            "v": "v",
            "w": "w",
            "x": "x",
            "y": "y",
            "z": "z",
            # Numbers
            "1": "One",
            "2": "Two",
            "3": "Three",
            "4": "Four",
            "5": "Five",
            "6": "Six",
            "7": "Seven",
            "8": "Eight",
            "9": "Nine",
            "10": "Ten",
            # Colors
            "red": "Red",
            "blue": "Blue",
            "green": "Green",
            "yellow": "Yellow",
            "purple": "Purple",
            # Shapes
            "circle": "Circle",
            "square": "Square",
            "triangle": "Triangle",
            "rectangle": "Rectangle",
            "pentagon": "Pentagon",
        }

        total_files = len(voice_texts)
        generated_count = 0

        print(f"🗣️ Generating {total_files} voice files using Windows TTS...")

        for filename, text in voice_texts.items():
            print(f'  Generating: {filename} -> "{text}"')

            success = self.generate_voice_wav(text, filename, rate=-1, volume=90)
            results[filename] = success

            if success:
                generated_count += 1
            else:
                print(f"    ❌ Failed to generate {filename}")

            # Small delay to avoid overwhelming the system
            time.sleep(0.1)

        print(f"✅ Voice generation complete: {generated_count}/{total_files} files generated")

        return results

    def is_available(self) -> bool:
        """Check if Windows TTS is available."""
        return self.tts_available


def test_windows_tts():
    """Test the Windows TTS generator."""
    print("Testing Windows TTS Generator...")

    # Get the sounds directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ss6_dir = os.path.dirname(script_dir)
    sounds_dir = os.path.join(ss6_dir, "sounds")

    # Create generator
    generator = WindowsTTSGenerator(sounds_dir)

    if not generator.is_available():
        print("❌ Windows TTS not available on this system")
        return False

    # Test generating a single voice
    print("Testing single voice generation...")
    if generator.generate_voice_wav("Hello World", "test_voice"):
        print("✅ Single voice generation successful")

        # Test playing the generated file
        try:
            pygame.mixer.init()
            test_sound = pygame.mixer.Sound(os.path.join(sounds_dir, "test_voice.wav"))
            print("🔊 Playing test voice...")
            test_sound.play()
            time.sleep(3)

            # Clean up test file
            os.remove(os.path.join(sounds_dir, "test_voice.wav"))

        except Exception as e:
            print(f"⚠️ Could not test playback: {e}")

        return True
    else:
        print("❌ Single voice generation failed")
        return False


if __name__ == "__main__":
    test_windows_tts()
