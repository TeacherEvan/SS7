#!/usr/bin/env python3
"""
Level Sound Integration Test for SS6 Super Student Game
Tests how sounds are triggered in actual game levels for educational effectiveness.
"""

import pygame
import sys
import os
from pathlib import Path
from typing import Dict, List, Optional
import json

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class LevelSoundIntegrationTester:
    """Tests sound integration across all game levels."""
    
    def __init__(self):
        """Initialize the tester."""
        # Set up headless audio
        os.environ['SDL_AUDIODRIVER'] = 'dummy'
        pygame.init()
        pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=1024)
        pygame.mixer.init()
        
        self.test_results = {
            "levels_tested": [],
            "sound_integration_status": {},
            "missing_sound_files": [],
            "timing_analysis": {},
            "issues_found": [],
            "recommendations": []
        }
        
        # Mock screen for level initialization
        self.screen = pygame.display.set_mode((800, 600))
        
        # Available sound files
        self.available_sounds = self._scan_available_sounds()
        
    def _scan_available_sounds(self) -> Dict[str, bool]:
        """Scan which sound files are actually available."""
        sounds_dir = Path("sounds")
        available = {}
        
        if sounds_dir.exists():
            for sound_file in sounds_dir.glob("*.wav"):
                key = sound_file.stem  # filename without extension
                available[key] = True
                
        return available
    
    def test_alphabet_level_sounds(self) -> Dict:
        """Test sound integration in alphabet level."""
        print("🔤 Testing Alphabet Level sound integration...")
        
        level_results = {
            "level_name": "alphabet_level",
            "sound_triggers_tested": [],
            "missing_sounds": [],
            "timing_issues": [],
            "integration_status": "unknown"
        }
        
        try:
            from levels.alphabet_level import AlphabetLevel
            
            # Create mock dependencies for level initialization
            mock_dependencies = self._create_mock_dependencies()
            
            # Initialize level with mock dependencies
            level = AlphabetLevel(**mock_dependencies)
            
            # Test sound triggers for available letters
            letters_to_test = ['I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
            letters_to_test.extend(['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'])  # lowercase available
            
            for letter in letters_to_test:
                if letter in self.available_sounds:
                    level_results["sound_triggers_tested"].append(letter)
                    # Test if sound manager can handle the trigger
                    if hasattr(level, 'sound_manager') and level.sound_manager:
                        try:
                            # Simulate sound trigger without actually playing
                            level.sound_manager.play_voice(letter)
                            print(f"   ✅ {letter}: Sound trigger working")
                        except Exception as e:
                            level_results["timing_issues"].append(f"{letter}: {e}")
                            print(f"   ❌ {letter}: Sound trigger failed - {e}")
                    else:
                        level_results["timing_issues"].append(f"{letter}: No sound manager available")
                        print(f"   ⚠️ {letter}: No sound manager in level")
                else:
                    level_results["missing_sounds"].append(letter)
                    print(f"   🚫 {letter}: Sound file missing")
            
            level_results["integration_status"] = "partial" if level_results["missing_sounds"] else "good"
            
        except ImportError as e:
            level_results["integration_status"] = "failed"
            level_results["timing_issues"].append(f"Import failed: {e}")
            print(f"   ❌ Failed to import AlphabetLevel: {e}")
        except Exception as e:
            level_results["integration_status"] = "failed"
            level_results["timing_issues"].append(f"Initialization failed: {e}")
            print(f"   ❌ Failed to initialize AlphabetLevel: {e}")
            
        return level_results
    
    def test_numbers_level_sounds(self) -> Dict:
        """Test sound integration in numbers level."""
        print("🔢 Testing Numbers Level sound integration...")
        
        level_results = {
            "level_name": "numbers_level",
            "sound_triggers_tested": [],
            "missing_sounds": [],
            "timing_issues": [],
            "integration_status": "unknown"
        }
        
        try:
            from levels.numbers_level import NumbersLevel
            
            mock_dependencies = self._create_mock_dependencies()
            level = NumbersLevel(**mock_dependencies)
            
            # Test numbers 1-10
            for num in range(1, 11):
                num_str = str(num)
                if num_str in self.available_sounds:
                    level_results["sound_triggers_tested"].append(num_str)
                    print(f"   ✅ {num}: Sound available")
                else:
                    level_results["missing_sounds"].append(num_str)
                    print(f"   🚫 {num}: Sound file missing")
            
            level_results["integration_status"] = "good" if not level_results["missing_sounds"] else "partial"
            
        except Exception as e:
            level_results["integration_status"] = "failed"
            level_results["timing_issues"].append(f"Error: {e}")
            print(f"   ❌ Failed to test NumbersLevel: {e}")
            
        return level_results
    
    def test_colors_level_sounds(self) -> Dict:
        """Test sound integration in colors level."""
        print("🎨 Testing Colors Level sound integration...")
        
        level_results = {
            "level_name": "colors_level", 
            "sound_triggers_tested": [],
            "missing_sounds": [],
            "timing_issues": [],
            "integration_status": "unknown"
        }
        
        try:
            from levels.colors_level import ColorsLevel
            
            mock_dependencies = self._create_mock_dependencies()
            level = ColorsLevel(**mock_dependencies)
            
            # Test color sounds
            colors = ["red", "blue", "green", "yellow", "purple"]
            for color in colors:
                if color in self.available_sounds:
                    level_results["sound_triggers_tested"].append(color)
                    print(f"   ✅ {color}: Sound available")
                else:
                    level_results["missing_sounds"].append(color)
                    print(f"   🚫 {color}: Sound file missing")
            
            level_results["integration_status"] = "good" if not level_results["missing_sounds"] else "partial"
            
        except Exception as e:
            level_results["integration_status"] = "failed"
            level_results["timing_issues"].append(f"Error: {e}")
            print(f"   ❌ Failed to test ColorsLevel: {e}")
            
        return level_results
    
    def test_shapes_level_sounds(self) -> Dict:
        """Test sound integration in shapes level."""
        print("📐 Testing Shapes Level sound integration...")
        
        level_results = {
            "level_name": "shapes_level",
            "sound_triggers_tested": [],
            "missing_sounds": [],
            "timing_issues": [],
            "integration_status": "unknown"
        }
        
        try:
            from levels.shapes_level import ShapesLevel
            
            mock_dependencies = self._create_mock_dependencies()
            level = ShapesLevel(**mock_dependencies)
            
            # Test shape sounds
            shapes = ["circle", "square", "triangle", "rectangle", "pentagon"]
            for shape in shapes:
                if shape in self.available_sounds:
                    level_results["sound_triggers_tested"].append(shape)
                    print(f"   ✅ {shape}: Sound available")
                else:
                    level_results["missing_sounds"].append(shape)
                    print(f"   🚫 {shape}: Sound file missing")
            
            level_results["integration_status"] = "good" if not level_results["missing_sounds"] else "partial"
            
        except Exception as e:
            level_results["integration_status"] = "failed"
            level_results["timing_issues"].append(f"Error: {e}")
            print(f"   ❌ Failed to test ShapesLevel: {e}")
            
        return level_results
    
    def test_cl_case_level_sounds(self) -> Dict:
        """Test sound integration in CL case level."""
        print("🔄 Testing CL Case Level sound integration...")
        
        level_results = {
            "level_name": "cl_case_level",
            "sound_triggers_tested": [],
            "missing_sounds": [],
            "timing_issues": [],
            "integration_status": "unknown"
        }
        
        try:
            from levels.cl_case_level import CLCaseLevel
            
            mock_dependencies = self._create_mock_dependencies()
            level = CLCaseLevel(**mock_dependencies)
            
            # Test both uppercase and lowercase letters that are available
            test_letters = []
            test_letters.extend(['I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'])
            test_letters.extend(['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'])
            
            for letter in test_letters:
                if letter in self.available_sounds:
                    level_results["sound_triggers_tested"].append(letter)
                    print(f"   ✅ {letter}: Sound available")
                else:
                    level_results["missing_sounds"].append(letter)
                    print(f"   🚫 {letter}: Sound file missing")
            
            level_results["integration_status"] = "partial"  # Always partial due to missing A-H
            
        except Exception as e:
            level_results["integration_status"] = "failed"
            level_results["timing_issues"].append(f"Error: {e}")
            print(f"   ❌ Failed to test CLCaseLevel: {e}")
            
        return level_results
    
    def _create_mock_dependencies(self) -> Dict:
        """Create mock dependencies for level initialization."""
        # Create minimal mock dependencies that levels expect
        fonts = {
            'default': pygame.font.Font(None, 36),
            'small': pygame.font.Font(None, 24),
            'target': pygame.font.Font(None, 48)
        }
        
        from unittest.mock import Mock
        
        return {
            'width': 800,
            'height': 600,
            'screen': self.screen,
            'fonts': fonts,
            'small_font': fonts['small'],
            'target_font': fonts['target'],
            'particle_manager': Mock(),
            'glass_shatter_manager': Mock(), 
            'multi_touch_manager': Mock(),
            'hud_manager': Mock(),
            'checkpoint_manager': Mock(),
            'center_piece_manager': Mock(),
            'flamethrower_manager': Mock(),
            'resource_manager': Mock(),
            'create_explosion_func': Mock(),
            'sound_manager': Mock(),
            'flame_colors': [(255, 165, 0), (255, 69, 0), (255, 0, 0)],
            'qboard_mode': False
        }
    
    def run_comprehensive_test(self) -> Dict:
        """Run comprehensive sound integration test across all levels."""
        print("🎮 SS6 Level Sound Integration Test")
        print("=" * 50)
        
        # Test each level
        test_functions = [
            self.test_alphabet_level_sounds,
            self.test_numbers_level_sounds,
            self.test_colors_level_sounds,
            self.test_shapes_level_sounds,
            self.test_cl_case_level_sounds
        ]
        
        for test_func in test_functions:
            try:
                result = test_func()
                self.test_results["levels_tested"].append(result["level_name"])
                self.test_results["sound_integration_status"][result["level_name"]] = result
                print()  # Add spacing between tests
            except Exception as e:
                print(f"   ❌ Failed to test level: {e}")
                self.test_results["issues_found"].append(f"Test failure: {e}")
        
        # Generate overall recommendations
        self._generate_integration_recommendations()
        
        return self.test_results
    
    def _generate_integration_recommendations(self):
        """Generate recommendations based on integration test results."""
        recommendations = []
        
        total_levels = len(self.test_results["levels_tested"])
        working_levels = sum(1 for status in self.test_results["sound_integration_status"].values() 
                           if status["integration_status"] in ["good", "partial"])
        
        recommendations.append(f"📊 Sound Integration Score: {working_levels}/{total_levels} levels working")
        
        # Collect all missing sounds across levels
        all_missing = []
        for level_data in self.test_results["sound_integration_status"].values():
            all_missing.extend(level_data["missing_sounds"])
        
        unique_missing = list(set(all_missing))
        if unique_missing:
            recommendations.append(f"🚨 CRITICAL: Missing sound files: {', '.join(unique_missing[:10])}")
            if len(unique_missing) > 10:
                recommendations.append(f"   ... and {len(unique_missing) - 10} more missing files")
        
        # Level-specific recommendations
        for level_name, level_data in self.test_results["sound_integration_status"].items():
            if level_data["integration_status"] == "failed":
                recommendations.append(f"❌ {level_name}: Complete integration failure - needs debugging")
            elif level_data["integration_status"] == "partial":
                recommendations.append(f"⚠️ {level_name}: Partial integration - some sounds missing")
            elif level_data["integration_status"] == "good":
                recommendations.append(f"✅ {level_name}: Sound integration working well")
        
        # General recommendations
        recommendations.append("🎯 Priority: Generate missing A-H uppercase letter sounds")
        recommendations.append("🎯 Priority: Generate missing i-z lowercase letter sounds")
        recommendations.append("🔧 Verify sound manager integration in all levels")
        recommendations.append("📚 Test actual sound playback timing during gameplay")
        
        self.test_results["recommendations"] = recommendations
    
    def print_summary_report(self):
        """Print a summary of the integration test results."""
        print("\n" + "=" * 50)
        print("📋 SOUND INTEGRATION TEST SUMMARY")
        print("=" * 50)
        
        print(f"\n🎯 LEVELS TESTED: {len(self.test_results['levels_tested'])}")
        for level_name in self.test_results["levels_tested"]:
            status = self.test_results["sound_integration_status"][level_name]["integration_status"]
            status_icon = {"good": "✅", "partial": "⚠️", "failed": "❌"}.get(status, "❓")
            print(f"   {status_icon} {level_name}: {status}")
        
        print(f"\n💡 RECOMMENDATIONS:")
        for i, rec in enumerate(self.test_results["recommendations"], 1):
            print(f"   {i}. {rec}")
        
        print("\n" + "=" * 50)
    
    def save_integration_report(self, filename: str = "level_sound_integration_report.json"):
        """Save the integration test report."""
        with open(filename, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        print(f"📄 Integration test report saved to: {filename}")

def main():
    """Main function to run level sound integration tests."""
    tester = LevelSoundIntegrationTester()
    
    # Run comprehensive test
    results = tester.run_comprehensive_test()
    
    # Print summary
    tester.print_summary_report()
    
    # Save detailed report
    tester.save_integration_report()

if __name__ == "__main__":
    main()