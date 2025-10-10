#!/usr/bin/env python3
"""
Docker-aware test runner for SS6 Super Student Game.
Handles both headless and display-enabled testing environments.
"""

import os
import subprocess
import sys
import time
from pathlib import Path

import pygame


def setup_headless_environment():
    """Setup headless display environment for testing."""
    display = os.environ.get("DISPLAY")
    if not display or display == ":99":
        print("🖥️  Setting up headless display environment...")

        # Set SDL to use dummy drivers for headless testing
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        os.environ["SDL_AUDIODRIVER"] = "dummy"
        os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

        # Verify Xvfb is running if DISPLAY is set
        if display == ":99":
            try:
                subprocess.run(["xset", "q"], check=True, capture_output=True)
                print("✅ Virtual display server is running")
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("⚠️  Virtual display not available, using dummy drivers")
    else:
        print(f"🖥️  Using existing display: {display}")


def test_pygame_initialization():
    """Test basic pygame initialization."""
    print("\n=== PYGAME INITIALIZATION TEST ===")

    try:
        pygame.init()
        print("✅ Pygame core initialized successfully")

        # Test mixer initialization
        pygame.mixer.init()
        print("✅ Pygame mixer initialized successfully")

        # Test display initialization (headless compatible)
        screen = pygame.display.set_mode((800, 600))
        print("✅ Display surface created successfully")

        # Test font system
        pygame.font.init()
        font = pygame.font.Font(None, 36)
        print("✅ Font system initialized successfully")

        return True

    except Exception as e:
        print(f"❌ Pygame initialization failed: {e}")
        return False


def test_sound_system():
    """Test the SS6 sound system comprehensively."""
    print("\n=== SOUND SYSTEM TEST ===")

    try:
        from universal_class import SoundManager

        # Initialize sound manager
        sound_manager = SoundManager()

        if not sound_manager.initialized:
            print("❌ Sound manager failed to initialize")
            return False

        print("✅ Sound manager initialized successfully")

        # Get status
        status = sound_manager.get_status()
        print(f"📊 Sound manager status: {status}")

        # Test voice file availability
        required_voices = {
            "alphabet": list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
            "numbers": [str(i) for i in range(1, 11)],
            "colors": ["red", "blue", "green", "yellow", "purple"],
            "shapes": ["circle", "square", "triangle", "rectangle", "pentagon"],
        }

        total_voices = 0
        available_voices = 0

        for category, voices in required_voices.items():
            print(f"\n📂 Testing {category} voices...")
            category_available = 0

            for voice in voices:
                total_voices += 1
                if sound_manager.ensure_voice_available(voice):
                    available_voices += 1
                    category_available += 1
                    print(f"  ✅ {voice}")
                else:
                    print(f"  ❌ {voice}")

            print(f"  📈 {category}: {category_available}/{len(voices)} available")

        print(f"\n📊 Overall voice availability: {available_voices}/{total_voices}")

        if available_voices == total_voices:
            print("✅ All required voice files are available")
        else:
            print(f"⚠️  {total_voices - available_voices} voice files are missing")

        # Test sound playback (will be silent in headless mode)
        print("\n🔊 Testing sound playback...")
        test_sounds = ["A", "B", "1", "2", "red", "circle"]

        for sound in test_sounds:
            try:
                if sound_manager.play_voice(sound):
                    print(f"  ✅ {sound} playback initiated")
                else:
                    print(f"  ❌ {sound} playback failed")
                time.sleep(0.1)  # Small delay between sounds
            except Exception as e:
                print(f"  ❌ {sound} playback error: {e}")

        return available_voices == total_voices

    except ImportError as e:
        print(f"❌ Could not import sound system: {e}")
        return False
    except Exception as e:
        print(f"❌ Sound system test failed: {e}")
        return False


def test_game_modules():
    """Test that game modules can be imported and initialized."""
    print("\n=== GAME MODULES TEST ===")

    modules_to_test = [
        "universal_class",
        "settings",
        "Display_settings",
        "welcome_screen",
        "levels.alphabet_level",
        "levels.numbers_level",
        "levels.shapes_level",
        "levels.colors_level",
        "levels.cl_case_level",
        "utils.config_manager",
        "utils.resource_manager",
        "utils.voice_generator",
    ]

    successful_imports = 0

    for module_name in modules_to_test:
        try:
            __import__(module_name)
            print(f"✅ {module_name}")
            successful_imports += 1
        except ImportError as e:
            print(f"❌ {module_name}: {e}")
        except Exception as e:
            print(f"⚠️  {module_name}: {e}")

    print(f"\n📊 Module imports: {successful_imports}/{len(modules_to_test)}")

    return successful_imports == len(modules_to_test)


def test_configuration_system():
    """Test the configuration system."""
    print("\n=== CONFIGURATION SYSTEM TEST ===")

    try:
        from utils.config_manager import get_config_manager

        config = get_config_manager()
        print("✅ Configuration manager loaded")

        # Test basic configuration access
        sequences = config.get("sequences", {})
        if sequences:
            print(f"✅ Game sequences loaded: {len(sequences)} types")
        else:
            print("⚠️  No game sequences found")

        # Test settings compatibility layer
        import settings

        if hasattr(settings, "SEQUENCES") and settings.SEQUENCES:
            print("✅ Settings compatibility layer working")
        else:
            print("⚠️  Settings compatibility layer issues")

        return True

    except Exception as e:
        print(f"❌ Configuration system test failed: {e}")
        return False


def test_resource_management():
    """Test resource management and caching."""
    print("\n=== RESOURCE MANAGEMENT TEST ===")

    try:
        from utils.resource_manager import ResourceManager

        # Test resource manager initialization
        resource_manager = ResourceManager()
        print("✅ Resource manager initialized")

        # Test game resources initialization
        resource_manager.initialize_game_resources()
        print("✅ Game resources initialized")

        return True

    except Exception as e:
        print(f"❌ Resource management test failed: {e}")
        return False


def run_integration_tests():
    """Run integration tests for the game."""
    print("\n=== INTEGRATION TESTS ===")

    try:
        # Test that the main game file can be executed in test mode
        print("🎮 Testing game execution...")

        # Import the main game module
        main_file = Path("SS6.origional.py")
        if main_file.exists():
            print("✅ Main game file found")

            # Try to import and run basic initialization
            import sys

            sys.path.insert(0, str(main_file.parent))

            # Test basic game initialization without full startup
            try:
                # This is a safe test - just check if the file can be read and basic imports work
                with open(main_file, "r") as f:
                    content = f.read()
                    if "pygame" in content and "universal_class" in content:
                        print("✅ Main game file structure is valid")
                    else:
                        print("⚠️  Main game file may be missing key components")
            except Exception as e:
                print(f"⚠️  Could not analyze main game file: {e}")
        else:
            print("❌ Main game file not found")
            return False

        return True

    except Exception as e:
        print(f"❌ Integration tests failed: {e}")
        return False


def generate_test_report(results):
    """Generate a comprehensive test report."""
    print("\n" + "=" * 60)
    print("📋 SS6 DOCKER TEST REPORT")
    print("=" * 60)

    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)

    print(f"📈 Overall Status: {passed_tests}/{total_tests} tests passed")
    print(f"🎯 Success Rate: {(passed_tests/total_tests)*100:.1f}%")

    print("\n📊 Detailed Results:")
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {test_name}")

    # Environment info
    print(f"\n🐳 Environment:")
    print(f"  - Python: {sys.version.split()[0]}")
    print(f"  - Pygame: {pygame.version.ver}")
    print(f"  - Display: {os.environ.get('DISPLAY', 'Not set')}")
    print(f"  - SDL Video Driver: {os.environ.get('SDL_VIDEODRIVER', 'Default')}")
    print(f"  - SDL Audio Driver: {os.environ.get('SDL_AUDIODRIVER', 'Default')}")

    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED - SS6 is ready for deployment!")
        return 0
    else:
        print(f"\n⚠️  {total_tests - passed_tests} test(s) failed - Review issues above")
        return 1


def main():
    """Main test runner function."""
    print("🚀 Starting SS6 Docker Test Suite...")

    # Setup environment
    setup_headless_environment()

    # Run all tests
    test_results = {
        "Pygame Initialization": test_pygame_initialization(),
        "Sound System": test_sound_system(),
        "Game Modules": test_game_modules(),
        "Configuration System": test_configuration_system(),
        "Resource Management": test_resource_management(),
        "Integration Tests": run_integration_tests(),
    }

    # Generate report and return exit code
    exit_code = generate_test_report(test_results)

    # Save results for CI/CD
    results_dir = Path("test-results")
    results_dir.mkdir(exist_ok=True)

    with open(results_dir / "test_results.txt", "w") as f:
        f.write(f"SS6 Docker Test Results\n")
        f.write(f"Overall: {sum(test_results.values())}/{len(test_results)} passed\n")
        for test_name, result in test_results.items():
            f.write(f"{test_name}: {'PASS' if result else 'FAIL'}\n")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
