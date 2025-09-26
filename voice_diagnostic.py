#!/usr/bin/env python3
"""
Voice system diagnostics script for SS6
"""

import sys
import os
sys.path.append(os.getcwd())
from universal_class import SoundManager
import pygame
pygame.init()

print('=== SOUND SYSTEM DIAGNOSTICS ===')
sound_manager = SoundManager()
print(f'Sound Manager Initialized: {sound_manager.initialized}')
print(f'Sound Manager Status: {sound_manager.get_status()}')

# Test voice availability
print('\n=== TESTING VOICE AVAILABILITY ===')
test_voices = ['a', 'A', '1', 'red', 'circle']
for voice in test_voices:
    available = sound_manager.ensure_voice_available(voice)
    print(f'Voice "{voice}": {"✓ Available" if available else "✗ Not Available"}')

# Test voice generation
print('\n=== TESTING VOICE GENERATION ===')
try:
    from utils.voice_generator import UniversalVoiceGenerator
    voice_gen = UniversalVoiceGenerator()
    print(f'ElevenLabs Available: {voice_gen.elevenlabs_available}')
    print(f'Windows TTS Available: {voice_gen.windows_tts_available}')
    print(f'Overall Available: {voice_gen.is_available()}')

    # Test a simple voice generation
    if voice_gen.is_available():
        test_result = voice_gen.generate_voice_file('Test', 'test_voice')
        print(f'Test voice generation: {"✓ Success" if test_result else "✗ Failed"}')
        
        # Check if the file was created
        sounds_dir = os.path.join(os.getcwd(), 'sounds')
        test_file = os.path.join(sounds_dir, 'test_voice.wav')
        if os.path.exists(test_file):
            print(f'Test file created: {test_file}')
        else:
            print('Test file not created')
    else:
        print('No voice generation methods available')
        
except Exception as e:
    print(f'Error testing voice generation: {e}')

# Check existing sound files
print('\n=== CHECKING EXISTING SOUND FILES ===')
sounds_dir = os.path.join(os.getcwd(), 'sounds')
if os.path.exists(sounds_dir):
    sound_files = [f for f in os.listdir(sounds_dir) if f.endswith('.wav')]
    print(f'Found {len(sound_files)} .wav files in sounds directory:')
    for f in sorted(sound_files)[:10]:  # Show first 10
        print(f'  - {f}')
    if len(sound_files) > 10:
        print(f'  ... and {len(sound_files) - 10} more')
else:
    print('Sounds directory not found')

# Test Windows TTS directly
print('\n=== TESTING WINDOWS TTS DIRECTLY ===')
try:
    from utils.windows_tts import WindowsTTSGenerator
    tts_gen = WindowsTTSGenerator(sounds_dir)
    print(f'Windows TTS Available: {tts_gen.is_available()}')
    
    if tts_gen.is_available():
        result = tts_gen.generate_voice_wav('Hello World', 'hello_test')
        print(f'Direct TTS test: {"✓ Success" if result else "✗ Failed"}')
        
        test_file = os.path.join(sounds_dir, 'hello_test.wav')
        if os.path.exists(test_file):
            print(f'Direct TTS file created: {test_file}')
        
except Exception as e:
    print(f'Error testing Windows TTS directly: {e}')
    import traceback
    traceback.print_exc()

print('\n=== DIAGNOSTICS COMPLETE ===')