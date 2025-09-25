# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import collect_data_files

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(SPEC))

block_cipher = None

# Collect all data files
datas = []

# Add sound files
sounds_dir = os.path.join(current_dir, 'sounds')
if os.path.exists(sounds_dir):
    for root, dirs, files in os.walk(sounds_dir):
        for file in files:
            if file.endswith(('.wav', '.mp3', '.ogg')):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, current_dir)
                datas.append((file_path, os.path.dirname(rel_path)))

# Add config files
config_dir = os.path.join(current_dir, 'config')
if os.path.exists(config_dir):
    for root, dirs, files in os.walk(config_dir):
        for file in files:
            if file.endswith(('.json', '.yaml', '.yml')):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, current_dir)
                datas.append((file_path, os.path.dirname(rel_path)))

# Add music files if they exist
music_dir = os.path.join(current_dir, 'music')
if os.path.exists(music_dir):
    for root, dirs, files in os.walk(music_dir):
        for file in files:
            if file.endswith(('.wav', '.mp3', '.ogg', '.mid', '.midi')):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, current_dir)
                datas.append((file_path, os.path.dirname(rel_path)))

# Add level progress file if it exists
level_progress = os.path.join(current_dir, 'level_progress.txt')
if os.path.exists(level_progress):
    datas.append((level_progress, '.'))

a = Analysis(
    ['SS6.origional.py'],
    pathex=[current_dir],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'pygame',
        'requests',
        'pyyaml',
        'psutil',
        'win32com.client',  # For Windows TTS
        'pyttsx3',  # Alternative TTS
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SuperStudent',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to False for windowed app
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path here if you have one
)