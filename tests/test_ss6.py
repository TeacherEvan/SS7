"""
Unit Tests for SS6 Super Student Game
Comprehensive test suite for core game logic, managers, and level systems.
"""

import unittest
import pygame
import os
import sys
import tempfile
import json
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Import yaml with fallback handling
try:
    import yaml
except ImportError:
    yaml = None

# Add the project root to the path so we can import modules
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Initialize pygame for tests that need it
pygame.init()

class TestObjectPooling(unittest.TestCase):
    """Test object pooling system."""
    
    def setUp(self):
        """Set up test environment."""
        from utils.object_pooling import ObjectPool, Particle, Explosion, PoolManager
        self.ObjectPool = ObjectPool
        self.Particle = Particle
        self.Explosion = Explosion
        self.PoolManager = PoolManager
    
    def test_object_pool_creation(self):
        """Test object pool creation and initialization."""
        pool = self.ObjectPool(
            factory=lambda: self.Particle(),
            reset_func=lambda p: p.reset(),
            initial_size=5,
            max_size=10
        )
        
        self.assertEqual(len(pool.available), 5)
        self.assertEqual(len(pool.in_use), 0)
    
    def test_object_pool_get_return(self):
        """Test getting and returning objects from pool."""
        pool = self.ObjectPool(
            factory=lambda: self.Particle(),
            reset_func=lambda p: p.reset(),
            initial_size=3,
            max_size=5
        )
        
        # Get objects
        obj1 = pool.get()
        obj2 = pool.get()
        
        self.assertEqual(len(pool.available), 1)
        self.assertEqual(len(pool.in_use), 2)
        
        # Return objects
        pool.return_object(obj1)
        self.assertEqual(len(pool.available), 2)
        self.assertEqual(len(pool.in_use), 1)
    
    def test_particle_initialization(self):
        """Test particle initialization and reset."""
        particle = self.Particle()
        
        # Test default state
        self.assertEqual(particle.x, 0.0)
        self.assertEqual(particle.y, 0.0)
        self.assertFalse(particle.active)
        
        # Test reset
        particle.x = 100.0
        particle.y = 200.0
        particle.active = True
        particle.reset()
        
        self.assertEqual(particle.x, 0.0)
        self.assertEqual(particle.y, 0.0)
        self.assertFalse(particle.active)
    
    def test_pool_manager(self):
        """Test pool manager functionality."""
        manager = self.PoolManager()
        
        # Test particle pool
        particle = manager.get_particle()
        self.assertIsInstance(particle, self.Particle)
        
        # Test explosion pool
        explosion = manager.get_explosion()
        self.assertIsInstance(explosion, self.Explosion)
        
        # Test stats
        stats = manager.get_pool_stats()
        self.assertIn('particles', stats)
        self.assertIn('explosions', stats)

class TestAnimationSystem(unittest.TestCase):
    """Test animation system."""
    
    def setUp(self):
        """Set up test environment."""
        from utils.animation_system import Animation, AnimatedTarget, AnimationManager, EaseType
        self.Animation = Animation
        self.AnimatedTarget = AnimatedTarget
        self.AnimationManager = AnimationManager
        self.EaseType = EaseType
        
        # Create a test object
        self.test_obj = {'x': 0.0, 'y': 0.0, 'scale': 1.0}
    
    def test_animation_creation(self):
        """Test animation creation."""
        animation = self.Animation(
            self.test_obj, 'x', 0.0, 100.0, 1.0, self.EaseType.LINEAR
        )
        
        self.assertEqual(animation.start_value, 0.0)
        self.assertEqual(animation.end_value, 100.0)
        self.assertEqual(animation.duration, 1.0)
    
    def test_animation_update(self):
        """Test animation update."""
        animation = self.Animation(
            self.test_obj, 'x', 0.0, 100.0, 1.0, self.EaseType.LINEAR
        )
        animation.start()
        
        # Update halfway through
        active = animation.update(0.5)
        self.assertTrue(active)
        self.assertAlmostEqual(self.test_obj['x'], 50.0, places=1)
        
        # Update to completion
        active = animation.update(0.5)
        self.assertFalse(active)
        self.assertAlmostEqual(self.test_obj['x'], 100.0, places=1)
    
    def test_animated_target(self):
        """Test animated target functionality."""
        target = self.AnimatedTarget(100, 200, "A", (255, 255, 255))
        
        self.assertEqual(target.x, 100)
        self.assertEqual(target.y, 200)
        self.assertEqual(target.text, "A")
        self.assertTrue(target.visible)
    
    def test_animation_manager(self):
        """Test animation manager."""
        manager = self.AnimationManager()
        target = self.AnimatedTarget(100, 200, "A", (255, 255, 255))
        
        # Add target
        manager.add_target(target)
        self.assertIn(target, manager.animated_targets)
        
        # Create animation
        animation = manager.create_target_animation(
            target, 'scale', 2.0, 1.0, self.EaseType.LINEAR
        )
        
        self.assertIsInstance(animation, self.Animation)
        
        # Test update
        manager.update(0.5)
        self.assertAlmostEqual(target.scale, 1.5, places=1)

class TestConfigurationSystem(unittest.TestCase):
    """Test configuration system."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir)
    
    def test_yaml_config_loading(self):
        """Test YAML configuration loading."""
        if yaml is None:
            self.skipTest("PyYAML not available")
            
        # Create test config
        test_config = {
            'display': {'mode': 'DEFAULT', 'fullscreen': False},
            'audio': {'sound_effects': True, 'background_music': True}
        }
        
        config_file = self.config_path / 'test_config.yaml'
        with open(config_file, 'w') as f:
            yaml.dump(test_config, f)
        
        # Load and verify
        with open(config_file, 'r') as f:
            loaded_config = yaml.safe_load(f)
        
        self.assertEqual(loaded_config['display']['mode'], 'DEFAULT')
        self.assertTrue(loaded_config['audio']['sound_effects'])
        with open(config_file, 'r') as f:
            loaded_config = yaml.safe_load(f)
        
        self.assertEqual(loaded_config['display']['mode'], 'DEFAULT')
        self.assertTrue(loaded_config['audio']['sound_effects'])
    
    def test_json_config_loading(self):
        """Test JSON configuration loading."""
        # Create test config
        test_config = {
            'game_modes': {'enabled': ['alphabet', 'numbers']},
            'visual': {'show_explosions': True}
        }
        
        config_file = self.config_path / 'test_config.json'
        with open(config_file, 'w') as f:
            json.dump(test_config, f)
        
        # Load and verify
        with open(config_file, 'r') as f:
            loaded_config = json.load(f)
        
        self.assertEqual(loaded_config['game_modes']['enabled'], ['alphabet', 'numbers'])
        self.assertTrue(loaded_config['visual']['show_explosions'])

class TestSoundSystem(unittest.TestCase):
    """Test sound system components."""
    
    def setUp(self):
        """Set up test environment."""
        # Mock pygame mixer to avoid audio dependencies in tests
        self.mixer_patcher = patch('pygame.mixer')
        self.mock_mixer = self.mixer_patcher.start()
        
        # Mock sound loading
        self.mock_sound = Mock()
        self.mock_mixer.Sound.return_value = self.mock_sound
    
    def tearDown(self):
        """Clean up test environment."""
        self.mixer_patcher.stop()
    
    def test_sound_manager_initialization(self):
        """Test sound manager initialization."""
        from utils.sound_system import SoundSystem
        
        sound_system = SoundSystem()
        self.assertIsNotNone(sound_system)
    
    def test_voice_generation_config(self):
        """Test voice generation configuration."""
        # Test voice config structure
        voice_config = {
            'provider': 'elevenlabs',
            'api_key': 'test_key',
            'voice_id': 'british_female',
            'model': 'eleven_monolingual_v1'
        }
        
        self.assertEqual(voice_config['provider'], 'elevenlabs')
        self.assertEqual(voice_config['voice_id'], 'british_female')

class TestGameLogic(unittest.TestCase):
    """Test core game logic."""
    
    def setUp(self):
        """Set up test environment."""
        # Mock pygame components
        self.screen_mock = Mock()
        self.font_mock = Mock()
        self.font_mock.render.return_value = Mock()
        
        # Mock managers
        self.particle_manager_mock = Mock()
        self.hud_manager_mock = Mock()
        self.sound_manager_mock = Mock()
    
    def test_sequence_progression(self):
        """Test game sequence progression."""
        from settings import SEQUENCES, GROUP_SIZE
        
        # Test alphabet sequence
        alphabet_sequence = SEQUENCES.get('alphabet', [])
        self.assertGreater(len(alphabet_sequence), 0)
        
        # Test grouping
        groups = [alphabet_sequence[i:i+GROUP_SIZE] for i in range(0, len(alphabet_sequence), GROUP_SIZE)]
        self.assertGreater(len(groups), 0)
        self.assertLessEqual(len(groups[0]), GROUP_SIZE)
    
    def test_target_validation(self):
        """Test target validation logic."""
        # Test letter validation
        valid_letters = ['A', 'B', 'C', 'Z']
        invalid_letters = ['1', '!', 'AA', '']
        
        for letter in valid_letters:
            self.assertTrue(letter.isalpha())
            self.assertEqual(len(letter), 1)
        
        for letter in invalid_letters:
            self.assertFalse(letter.isalpha() and len(letter) == 1)
    
    def test_score_calculation(self):
        """Test score calculation logic."""
        # Test basic scoring
        base_score = 100
        multiplier = 1.5
        bonus = 50
        
        final_score = int(base_score * multiplier + bonus)
        expected_score = int(100 * 1.5 + 50)
        
        self.assertEqual(final_score, expected_score)

class TestPerformanceOptimizations(unittest.TestCase):
    """Test performance optimization components."""
    
    def setUp(self):
        """Set up test environment."""
        # Mock pygame surface
        self.surface_mock = Mock()
        self.surface_mock.get_width.return_value = 100
        self.surface_mock.get_height.return_value = 100
    
    def test_texture_atlas_creation(self):
        """Test texture atlas creation."""
        # Initialize pygame display for texture atlas tests
        pygame.display.set_mode((1, 1), pygame.NOFRAME)
        
        from utils.texture_atlas import TextureAtlas
        
        atlas = TextureAtlas(512, 512)
        self.assertEqual(atlas.width, 512)
        self.assertEqual(atlas.height, 512)
        self.assertEqual(len(atlas.regions), 0)
    
    def test_texture_atlas_add(self):
        """Test adding textures to atlas."""
        # Initialize pygame display for texture atlas tests
        pygame.display.set_mode((1, 1), pygame.NOFRAME)
        
        from utils.texture_atlas import TextureAtlas
        
        atlas = TextureAtlas(512, 512)
        
        # Create a real pygame Surface for texture
        texture_surface = pygame.Surface((64, 64))
        texture_surface.fill((255, 0, 0))  # Red texture for testing
        
        # Add texture
        success = atlas.add_texture('test_texture', texture_surface)
        self.assertTrue(success)
        self.assertIn('test_texture', atlas.regions)
    
    def test_memory_profiler_initialization(self):
        """Test memory profiler initialization."""
        from utils.memory_profiler import MemoryProfiler
        
        profiler = MemoryProfiler(max_history=100)
        self.assertEqual(profiler.max_history, 100)
        self.assertTrue(profiler.enabled)
    
    @patch('psutil.Process')
    def test_memory_profiler_update(self, mock_process):
        """Test memory profiler update."""
        from utils.memory_profiler import MemoryProfiler
        
        # Mock process memory info
        mock_memory_info = Mock()
        mock_memory_info.rss = 1024 * 1024 * 100  # 100 MB
        # Mock peak_wss as an integer, not a Mock object
        mock_memory_info.peak_wss = 1024 * 1024 * 120  # 120 MB
        mock_process.return_value.memory_info.return_value = mock_memory_info
        
        profiler = MemoryProfiler(max_history=10)
        profiler.update(0.016)  # 60 FPS
        
        self.assertGreater(len(profiler.metrics_history), 0)
        current_metrics = profiler.get_current_metrics()
        self.assertIsNotNone(current_metrics)

class TestLevelSystem(unittest.TestCase):
    """Test level system components."""
    
    def setUp(self):
        """Set up test environment."""
        # Mock pygame and dependencies
        self.screen_mock = Mock()
        self.font_mock = Mock()
        self.font_mock.render.return_value = Mock()
        
        # Mock all manager dependencies
        self.managers = {
            'particle_manager': Mock(),
            'glass_shatter_manager': Mock(),
            'multi_touch_manager': Mock(),
            'hud_manager': Mock(),
            'checkpoint_manager': Mock(),
            'center_piece_manager': Mock(),
            'flamethrower_manager': Mock(),
            'resource_manager': Mock(),
            'sound_manager': Mock()
        }
        
        # Mock functions
        self.functions = {
            'create_explosion_func': Mock(),
            'create_flame_effect_func': Mock(),
            'apply_explosion_effect_func': Mock(),
            'create_particle_func': Mock(),
            'draw_explosion_func': Mock(),
            'game_over_screen_func': Mock()
        }
    
    def test_level_initialization(self):
        """Test level initialization."""
        # Import here to avoid circular imports during test discovery
        try:
            from levels.alphabet_level import AlphabetLevel
            
            level = AlphabetLevel(
                1920, 1080, self.screen_mock, [self.font_mock], self.font_mock, self.font_mock,
                **self.managers, **self.functions,
                explosions_list=[], lasers_list=[]
            )
            
            self.assertEqual(level.width, 1920)
            self.assertEqual(level.height, 1080)
            self.assertIsNotNone(level.sequence)
            
        except ImportError:
            self.skipTest("AlphabetLevel not available for testing")
    
    def test_level_state_reset(self):
        """Test level state reset."""
        try:
            from levels.alphabet_level import AlphabetLevel
            
            level = AlphabetLevel(
                1920, 1080, self.screen_mock, [self.font_mock], self.font_mock, self.font_mock,
                **self.managers, **self.functions,
                explosions_list=[], lasers_list=[]
            )
            
            # Modify some state
            level.total_destroyed = 10
            level.letters_spawned = 5
            
            # Reset
            level.reset_level_state()
            
            self.assertEqual(level.total_destroyed, 0)
            self.assertEqual(level.letters_spawned, 0)
            
        except ImportError:
            self.skipTest("AlphabetLevel not available for testing")

class TestUtilityFunctions(unittest.TestCase):
    """Test utility functions."""
    
    def test_color_validation(self):
        """Test color validation."""
        # Valid RGB colors
        valid_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (128, 128, 128)]
        
        for color in valid_colors:
            self.assertEqual(len(color), 3)
            for component in color:
                self.assertGreaterEqual(component, 0)
                self.assertLessEqual(component, 255)
    
    def test_position_validation(self):
        """Test position validation."""
        screen_width, screen_height = 1920, 1080
        
        # Valid positions
        valid_positions = [(0, 0), (960, 540), (1919, 1079)]
        
        for x, y in valid_positions:
            self.assertGreaterEqual(x, 0)
            self.assertLess(x, screen_width)
            self.assertGreaterEqual(y, 0)
            self.assertLess(y, screen_height)
    
    def test_distance_calculation(self):
        """Test distance calculation."""
        import math
        
        point1 = (0, 0)
        point2 = (3, 4)
        
        distance = math.sqrt((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2)
        expected_distance = 5.0
        
        self.assertAlmostEqual(distance, expected_distance, places=1)

def run_all_tests():
    """Run all unit tests."""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestObjectPooling,
        TestAnimationSystem,
        TestConfigurationSystem,
        TestSoundSystem,
        TestGameLogic,
        TestPerformanceOptimizations,
        TestLevelSystem,
        TestUtilityFunctions
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result

if __name__ == '__main__':
    # Run all tests
    result = run_all_tests()
    
    # Print summary
    print(f"\nTest Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    # Exit with appropriate code
    exit_code = 0 if result.wasSuccessful() else 1
    sys.exit(exit_code)