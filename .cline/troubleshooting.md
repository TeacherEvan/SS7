# Troubleshooting Guide - SS6 Super Student Game

## Common Issues and Solutions

### 1. Installation Problems

#### Pygame Installation Fails

```bash
# Manual pygame installation if install.py fails
pip install pygame==2.0.0

# Verify installation
python -c "import pygame; print(pygame.version)"
```

**Symptoms:**

- ImportError: No module named 'pygame'
- Failed to install pygame via install.py

**Solutions:**

1. Check Python version (requires 3.6+)
2. Install Visual C++ Build Tools (Windows)
3. Use `pip install --only-binary=all pygame` (Windows)
4. Try `python -m pip install pygame` instead of pip

#### Missing Dependencies

```bash
# Install all requirements manually
pip install pygame requests pyyaml psutil

# For voice features (optional)
pip install elevenlabs
```

### 2. Display Issues

#### Game Won't Launch in Fullscreen

```python
# Debug display initialization
try:
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
    print(f"Fullscreen mode: {pygame.display.get_surface().get_size()}")
except pygame.error as e:
    print(f"Fullscreen failed: {e}")
    # Fallback to windowed
    screen = pygame.display.set_mode((800, 600))
```

**Symptoms:**

- Pygame window doesn't appear
- "No available video device" error
- Display mode detection fails

**Solutions:**

1. Check display drivers and resolution
2. Run `python Display_settings.py` to test display detection
3. Try windowed mode: `python SS6.origional.py --windowed`
4. Verify pygame.display initialization order

#### QBOARD Mode Not Detected

```python
# Debug display mode detection
from Display_settings import detect_display_type, PERFORMANCE_SETTINGS

print(f"Detected display: {detect_display_type()}")
print(f"Available modes: {list(PERFORMANCE_SETTINGS.keys())}")

# Test manual mode setting
import os
os.environ['DISPLAY_MODE'] = 'QBOARD'
```

**Solutions:**

1. Check `Display_settings.py` for detection logic
2. Manually set display mode for testing
3. Verify touch/multi-touch capabilities
4. Check display resolution and aspect ratio

### 3. Audio Problems

#### No Sound Output

```python
# Debug audio initialization
import pygame

pygame.mixer.init()
print(f"Mixer initialized: {pygame.mixer.get_init()}")
print(f"Default frequency: {pygame.mixer.get_init()[0]}")

# Test sound loading
try:
    sound = pygame.mixer.Sound('sounds/a.wav')
    print(f"Sound loaded: {sound.get_length()} seconds")
except Exception as e:
    print(f"Sound loading failed: {e}")
```

**Symptoms:**

- No audio during gameplay
- Voice generation fails silently
- Sound files won't load

**Solutions:**

1. Check audio drivers and default playback device
2. Verify pygame.mixer initialization
3. Test with simple sound file first
4. Check file permissions on sounds directory
5. Verify sound file formats (WAV only)

#### Voice Generation Failures

**ElevenLabs API Issues:**

```python
# Test API connectivity
import requests

try:
    response = requests.get('https://api.elevenlabs.io/v1/voices', timeout=5)
    print(f"API Status: {response.status_code}")
except Exception as e:
    print(f"API Error: {e}")
```

**Windows SAPI Issues:**

```python
# Test SAPI availability
try:
    import win32com.client
    speaker = win32com.client.Dispatch("SAPI.SpVoice")
    speaker.Speak("Test")
    print("SAPI working")
except ImportError:
    print("SAPI not available - need pywin32")
except Exception as e:
    print(f"SAPI error: {e}")
```

**Solutions:**

1. Check ElevenLabs API key in `config/voice_config.json`
2. Verify internet connectivity for API calls
3. Install pywin32 for SAPI support: `pip install pywin32`
4. Test with simple text first
5. Check voice file permissions and disk space

### 4. Configuration Issues

#### Configuration Files Not Loading

```python
# Debug configuration loading
import json
import yaml

try:
    with open('config/game_config.json', 'r') as f:
        config = json.load(f)
    print(f"Game config loaded: {len(config)} keys")
except Exception as e:
    print(f"Game config error: {e}")

try:
    with open('config/teacher_config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    print(f"Teacher config loaded: {len(config)} keys")
except Exception as e:
    print(f"Teacher config error: {e}")
```

**Symptoms:**

- Default settings used instead of custom config
- JSON/YAML parsing errors
- Configuration changes ignored

**Solutions:**

1. Check file permissions on config files
2. Validate JSON/YAML syntax
3. Verify config file paths and locations
4. Check for BOM or encoding issues
5. Test with minimal config files

#### Legacy Settings Conflicts

```python
# Check for settings conflicts
try:
    from settings import SEQUENCES, FONT_SIZES
    print(f"Legacy sequences: {len(SEQUENCES)}")
    print(f"Legacy fonts: {FONT_SIZES}")
except Exception as e:
    print(f"Legacy settings error: {e}")

# Compare with new config
from utils.config_manager import get_config_manager
config = get_config_manager()
new_sequences = config.get('sequences', {})
```

### 5. Performance Issues

#### Low Frame Rates

```python
# Profile performance
import cProfile

# Profile main game loop
cProfile.run('run_game()', sort='cumulative')

# Memory profiling
import psutil
import os

process = psutil.Process(os.getpid())
print(f"Memory usage: {process.memory_info().rss / 1024 / 1024:.1f} MB")
```

**Symptoms:**

- Game runs slower than expected
- Choppy animations or input lag
- High CPU/memory usage

**Solutions:**

1. Check display mode optimization (QBOARD vs DEFAULT)
2. Reduce particle counts in configuration
3. Verify hardware acceleration is enabled
4. Check for memory leaks in custom code
5. Profile and optimize expensive operations

#### Memory Leaks

```python
# Monitor memory usage over time
import gc
import time

def monitor_memory():
    gc.collect()
    print(f"Objects: {len(gc.get_objects())}")

    process = psutil.Process(os.getpid())
    memory_mb = process.memory_info().rss / 1024 / 1024
    print(f"Memory: {memory_mb:.1f} MB")

# Monitor during gameplay
for i in range(10):
    monitor_memory()
    time.sleep(5)
```

### 6. Level Loading Problems

#### Manager Initialization Failures

```python
# Debug manager creation
try:
    from universal_class import *
    print("Universal managers imported successfully")

    # Test manager instantiation
    managers = create_universal_managers()
    print(f"Managers created: {len(managers)}")

except Exception as e:
    print(f"Manager creation failed: {e}")
    import traceback
    traceback.print_exc()
```

**Symptoms:**

- Levels fail to initialize
- Manager dependency errors
- Import errors in level files

**Solutions:**

1. Check universal_class.py for syntax errors
2. Verify all manager dependencies are available
3. Check circular import issues
4. Test manager creation in isolation
5. Verify constructor signatures match

#### Resource Loading Failures

```python
# Debug resource loading
try:
    from utils.resource_manager import ResourceManager
    rm = ResourceManager()

    # Test font loading
    font = rm.get_font(48, 'DEFAULT')
    print(f"Font loaded: {font}")

    # Test surface caching
    surface = rm.get_center_target(48)
    print(f"Surface created: {surface.get_size()}")

except Exception as e:
    print(f"Resource loading failed: {e}")
```

### 7. File System Issues

#### Missing Sound Files

```bash
# Check sound directory
ls -la sounds/

# Count expected vs actual files
python -c "
import os
sound_dir = 'sounds'
expected_files = ['a.wav', 'b.wav', 'welcome_male.wav']  # etc
missing = []

for file in expected_files:
    if not os.path.exists(os.path.join(sound_dir, file)):
        missing.append(file)

print(f'Missing files: {missing}')
"
```

**Solutions:**

1. Run `python generate_all_sounds.py` to create missing sounds
2. Check voice generation system functionality
3. Verify disk space and write permissions
4. Check for antivirus interference with file creation

#### Configuration File Permissions

```bash
# Check file permissions
import os
import stat

config_files = ['config/game_config.json', 'config/teacher_config.yaml']
for file in config_files:
    if os.path.exists(file):
        mode = os.stat(file).st_mode
        print(f"{file}: {stat.filemode(mode)}")
    else:
        print(f"{file}: NOT FOUND")
```

### 8. Development Environment Issues

#### Import Path Problems

```python
# Debug Python path
import sys
print("Python path:")
for p in sys.path:
    print(f"  {p}")

# Test imports from project root
try:
    from levels.alphabet_level import AlphabetLevel
    print("Level import successful")
except ImportError as e:
    print(f"Level import failed: {e}")
```

**Solutions:**

1. Run from project root directory
2. Check PYTHONPATH environment variable
3. Verify all files are in correct locations
4. Check for naming conflicts

#### IDE Integration Issues

```python
# Test basic pygame functionality
import pygame
pygame.init()
print(f"Pygame version: {pygame.version.ver}")

# Test display creation
screen = pygame.display.set_mode((400, 300))
print(f"Display created: {screen.get_size()}")

pygame.quit()
```

## Emergency Debugging Procedures

### 1. Reset to Clean State

```bash
# Clean all generated files
rm -f sounds/*.wav
rm -f config/game_config.json
rm -f config/teacher_config.yaml
rm -f level_progress.txt

# Reinstall from scratch
python install.py
```

### 2. Minimal Test Case

```python
# Create minimal reproduction
import pygame
pygame.init()

# Test basic functionality
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
```

### 3. Component Isolation Testing

```python
# Test each system independently
def test_systems():
    # Test 1: Display
    print("Testing display...")
    # Test display code

    # Test 2: Audio
    print("Testing audio...")
    # Test audio code

    # Test 3: Configuration
    print("Testing configuration...")
    # Test config code

    # Test 4: Managers
    print("Testing managers...")
    # Test manager code
```

## Getting Help

### Debug Information Collection

```python
def collect_debug_info():
    """Collect comprehensive debug information"""
    info = {
        'python_version': sys.version,
        'pygame_version': pygame.version.ver if 'pygame' in globals() else 'Not installed',
        'platform': sys.platform,
        'current_directory': os.getcwd(),
        'display_mode': 'Unknown',
        'config_files': {},
        'sound_files': 0
    }

    # Check display mode
    try:
        from Display_settings import detect_display_type
        info['display_mode'] = detect_display_type()
    except:
        pass

    # Check config files
    for file in ['config/game_config.json', 'config/teacher_config.yaml']:
        info['config_files'][file] = os.path.exists(file)

    # Count sound files
    if os.path.exists('sounds'):
        info['sound_files'] = len([f for f in os.listdir('sounds') if f.endswith('.wav')])

    return info

# Print debug info
import sys, os
debug_info = collect_debug_info()
for key, value in debug_info.items():
    print(f"{key}: {value}")
```

### Log Analysis

```python
# Enable detailed logging
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='debug.log'
)

logger = logging.getLogger(__name__)

# Add logging to critical sections
def critical_function():
    logger.info("Entering critical function")
    try:
        # Function logic
        logger.info("Function completed successfully")
    except Exception as e:
        logger.error(f"Function failed: {e}")
        raise
```

This troubleshooting guide covers the most common issues encountered when working with the SS6 project. Use the debug information collection and systematic testing approaches to quickly identify and resolve problems.
