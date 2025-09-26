#!/usr/bin/env python3
"""
Smart Voice Assignment System for SS6 Super Student Game
Handles intelligent voice selection based on context, level type, and content.
"""

import json
import os
import random
from typing import Dict, Optional, Tuple
from enum import Enum

class ContentType(Enum):
    """Types of content that can be spoken."""
    LETTER = "letter"
    EMOJI = "emoji"
    NUMBER = "number"
    COLOR = "color"
    SHAPE = "shape"
    GENERAL = "general"
    TARGET_HIT = "target_hit"

class LevelType(Enum):
    """Game level types."""
    ALPHABET = "alphabet_level"
    NUMBERS = "numbers_level"
    COLORS = "colors_level"
    SHAPES = "shapes_level"
    CL_CASE = "cl_case_level"

class VoiceAssignmentSystem:
    """
    Intelligent system for assigning voices based on context and rules.
    """
    
    def __init__(self, config_path: str = None):
        """Initialize the voice assignment system."""
        if config_path is None:
            config_path = os.path.join("config", "voice_config.json")
        
        self.config_path = config_path
        self.config = self._load_config()
        self.assignment_rules = self.config.get("voice_assignment_rules", {})
        self.available_voices = self.config.get("available_voices", {})
        
        # Initialize random seed for consistent testing if needed
        random.seed()
    
    def _load_config(self) -> Dict:
        """Load voice configuration from file."""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading voice config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Get default configuration if loading fails."""
        return {
            "available_voices": {
                "female_default": {"id": "21m00Tcm4TlvDq8ikWAM"},
                "male_elderly_stoic": {"id": "APpgW59845BoO9h8iuwQ"}
            },
            "voice_assignment_rules": {
                "default_voice": "female_default"
            }
        }
    
    def get_voice_for_content(self, 
                            level_type: LevelType, 
                            content_type: ContentType, 
                            content: str = "",
                            context: str = "") -> Tuple[str, Dict]:
        """
        Get the appropriate voice ID and settings for given content.
        
        Args:
            level_type: The type of game level
            content_type: The type of content being spoken
            content: The actual content to be spoken
            context: Additional context (e.g., "target_destroyed", "emoji_name")
            
        Returns:
            Tuple of (voice_key, voice_config) where voice_config contains id and settings
        """
        
        # Handle emoji pronunciations in alphabet and case levels
        if (content_type == ContentType.EMOJI and 
            level_type in [LevelType.ALPHABET, LevelType.CL_CASE]):
            return self._get_emoji_voice(level_type)
        
        # Handle percentage-based voice selection for colors and shapes
        if (level_type in [LevelType.COLORS, LevelType.SHAPES] and
            content_type == ContentType.TARGET_HIT):
            return self._get_percentage_based_voice(level_type)
        
        # Default to level-specific voice or general default
        return self._get_default_voice_for_level(level_type)
    
    def _get_emoji_voice(self, level_type: LevelType) -> Tuple[str, Dict]:
        """Get voice for emoji pronunciations in alphabet/case levels."""
        emoji_rules = self.assignment_rules.get("emoji_pronunciations", {})
        voice_key = emoji_rules.get(level_type.value, "male_elderly_stoic")
        
        if voice_key not in self.available_voices:
            voice_key = "male_elderly_stoic"
        
        return voice_key, self.available_voices[voice_key]
    
    def _get_percentage_based_voice(self, level_type: LevelType) -> Tuple[str, Dict]:
        """Get voice based on percentage rules for colors/shapes levels."""
        percentage_rules = self.assignment_rules.get("percentage_based", {})
        level_rules = percentage_rules.get(level_type.value, {})
        
        if not level_rules:
            # Default to 40% male, 60% female
            level_rules = {
                "male_elderly_stoic": 40,
                "female_default": 60
            }
        
        # Generate random number (0-99) for proper percentage distribution
        rand_num = random.randint(0, 99)
        
        # Get the male percentage threshold
        male_percentage = level_rules.get("male_elderly_stoic", 40)
        
        # Simple logic: if random < male_percentage, use male; otherwise use female
        if rand_num < male_percentage:
            voice_key = "male_elderly_stoic"
        else:
            voice_key = "female_default"
        
        # For debugging - remove this later
        # print(f"Debug: rand={rand_num}, threshold={male_percentage}, selected={voice_key}")
        
        # Ensure the selected voice exists
        if voice_key in self.available_voices:
            return voice_key, self.available_voices[voice_key]
        
        # Fallback to default
        return self._get_default_voice()
    
    def _get_default_voice_for_level(self, level_type: LevelType) -> Tuple[str, Dict]:
        """Get default voice for a specific level type."""
        level_defaults = self.assignment_rules.get("level_defaults", {})
        voice_key = level_defaults.get(level_type.value)
        
        if voice_key and voice_key in self.available_voices:
            return voice_key, self.available_voices[voice_key]
        
        return self._get_default_voice()
    
    def _get_default_voice(self) -> Tuple[str, Dict]:
        """Get the system default voice."""
        default_key = self.assignment_rules.get("default_voice", "female_default")
        
        if default_key in self.available_voices:
            return default_key, self.available_voices[default_key]
        
        # Ultimate fallback
        first_voice = list(self.available_voices.keys())[0]
        return first_voice, self.available_voices[first_voice]
    
    def test_voice_assignments(self):
        """Test the voice assignment system with various scenarios."""
        print("🎤 Testing Voice Assignment System")
        print("=" * 50)
        
        test_scenarios = [
            # (level_type, content_type, content, context, description)
            (LevelType.ALPHABET, ContentType.LETTER, "A", "", "Alphabet letter"),
            (LevelType.ALPHABET, ContentType.EMOJI, "apple", "emoji", "Alphabet emoji"),
            (LevelType.CL_CASE, ContentType.LETTER, "a", "", "Case letter"),
            (LevelType.CL_CASE, ContentType.EMOJI, "ant", "emoji", "Case emoji"),
            (LevelType.COLORS, ContentType.TARGET_HIT, "red", "target_destroyed", "Color target hit"),
            (LevelType.SHAPES, ContentType.TARGET_HIT, "circle", "target_destroyed", "Shape target hit"),
            (LevelType.NUMBERS, ContentType.NUMBER, "5", "", "Number"),
            (LevelType.COLORS, ContentType.COLOR, "blue", "", "Color name"),
        ]
        
        for level_type, content_type, content, context, description in test_scenarios:
            voice_key, voice_config = self.get_voice_for_content(
                level_type, content_type, content, context
            )
            voice_name = voice_config.get("name", voice_key)
            print(f"📝 {description:20} → {voice_name}")
        
        # Test percentage distribution
        print("\n🎲 Testing Percentage Distribution (Colors Level)")
        print("-" * 40)
        male_count = 0
        female_count = 0
        total_tests = 100
        
        for i in range(total_tests):
            voice_key, _ = self.get_voice_for_content(
                LevelType.COLORS, ContentType.TARGET_HIT, "red", "target_destroyed"
            )
            if voice_key == "male_elderly_stoic":
                male_count += 1
            else:
                female_count += 1
        
        male_percent = (male_count / total_tests) * 100
        female_percent = (female_count / total_tests) * 100
        
        print(f"Male voice:   {male_count:3d}/100 ({male_percent:5.1f}%) - Target: 40%")
        print(f"Female voice: {female_count:3d}/100 ({female_percent:5.1f}%) - Target: 60%")
        
        print("\n✅ Voice assignment system test complete!")

def main():
    """Test the voice assignment system."""
    vas = VoiceAssignmentSystem()
    vas.test_voice_assignments()

if __name__ == "__main__":
    main()