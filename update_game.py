#!/usr/bin/env python3
"""
SS6 Auto-Update System
Checks for and downloads updates from GitHub repository.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from urllib.parse import urlparse

import requests

# Configuration
GITHUB_REPO = "TeacherEvan/SS7"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}"
VERSION_FILE = "version.json"
BACKUP_DIR = "backup"


class GameUpdater:
    def __init__(self):
        self.current_version = self.get_current_version()
        self.script_dir = os.path.dirname(os.path.abspath(__file__))

    def get_current_version(self):
        """Get current installed version."""
        version_path = os.path.join(os.path.dirname(__file__), VERSION_FILE)
        if os.path.exists(version_path):
            try:
                with open(version_path, "r") as f:
                    data = json.load(f)
                    return data.get("version", "1.0.0")
            except:
                pass
        return "1.0.0"  # Default version

    def check_for_updates(self):
        """Check if updates are available on GitHub."""
        try:
            print("🔍 Checking for updates...")
            response = requests.get(f"{GITHUB_API_URL}/releases/latest", timeout=10)
            if response.status_code == 200:
                release_info = response.json()
                latest_version = release_info["tag_name"].lstrip("v")

                print(f"📦 Current version: {self.current_version}")
                print(f"🆕 Latest version: {latest_version}")

                if latest_version != self.current_version:
                    return {
                        "available": True,
                        "version": latest_version,
                        "download_url": None,  # We'll get this from assets
                        "release_notes": release_info.get("body", "No release notes available."),
                        "assets": release_info.get("assets", []),
                    }
                else:
                    print("✅ You have the latest version!")
                    return {"available": False}
            else:
                print(f"❌ Failed to check for updates: HTTP {response.status_code}")
                return {"available": False, "error": f"HTTP {response.status_code}"}
        except requests.RequestException as e:
            print(f"❌ Network error checking for updates: {e}")
            return {"available": False, "error": str(e)}
        except Exception as e:
            print(f"❌ Error checking for updates: {e}")
            return {"available": False, "error": str(e)}

    def download_update(self, update_info):
        """Download and apply the update."""
        # Find the appropriate asset (game zip file)
        download_url = None
        for asset in update_info.get("assets", []):
            if asset["name"].endswith(".zip") and "SuperStudent" in asset["name"]:
                download_url = asset["browser_download_url"]
                break

        if not download_url:
            print("❌ No downloadable game package found in release.")
            return False

        try:
            print(f"⬇️  Downloading update from: {download_url}")

            # Create temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                zip_path = os.path.join(temp_dir, "update.zip")

                # Download the update
                response = requests.get(download_url, stream=True, timeout=30)
                response.raise_for_status()

                with open(zip_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)

                print("📦 Download complete, extracting...")

                # Create backup of current version
                self.create_backup()

                # Extract and apply update
                with zipfile.ZipFile(zip_path, "r") as zip_ref:
                    extract_dir = os.path.join(temp_dir, "extracted")
                    zip_ref.extractall(extract_dir)

                    # Find the extracted game files
                    game_files = []
                    for root, dirs, files in os.walk(extract_dir):
                        for file in files:
                            if file.endswith((".py", ".exe", ".bat", ".sh")):
                                game_files.append(os.path.join(root, file))

                    # Copy new files to game directory
                    for file_path in game_files:
                        rel_path = os.path.relpath(file_path, extract_dir)
                        dest_path = os.path.join(self.script_dir, rel_path)

                        # Ensure destination directory exists
                        os.makedirs(os.path.dirname(dest_path), exist_ok=True)

                        # Copy file
                        shutil.copy2(file_path, dest_path)
                        print(f"✅ Updated: {rel_path}")

                # Update version file
                self.save_version(update_info["version"])

                print(f"🎉 Successfully updated to version {update_info['version']}!")
                print("\n📋 Release Notes:")
                print(update_info.get("release_notes", "No release notes available."))

                return True

        except Exception as e:
            print(f"❌ Error during update: {e}")
            print("🔄 Restoring from backup...")
            self.restore_backup()
            return False

    def create_backup(self):
        """Create backup of current game files."""
        backup_path = os.path.join(self.script_dir, BACKUP_DIR)
        if os.path.exists(backup_path):
            shutil.rmtree(backup_path)

        os.makedirs(backup_path, exist_ok=True)

        # Backup important files
        important_files = [
            "SS6.origional.py",
            "settings.py",
            "universal_class.py",
            "welcome_screen.py",
            "levels/",
            "utils/",
            "config/",
        ]

        for item in important_files:
            src = os.path.join(self.script_dir, item)
            if os.path.exists(src):
                dest = os.path.join(backup_path, item)
                if os.path.isdir(src):
                    shutil.copytree(src, dest)
                else:
                    shutil.copy2(src, dest)

        print("💾 Backup created successfully.")

    def restore_backup(self):
        """Restore from backup if update fails."""
        backup_path = os.path.join(self.script_dir, BACKUP_DIR)
        if not os.path.exists(backup_path):
            print("❌ No backup found to restore.")
            return False

        try:
            for item in os.listdir(backup_path):
                src = os.path.join(backup_path, item)
                dest = os.path.join(self.script_dir, item)

                if os.path.exists(dest):
                    if os.path.isdir(dest):
                        shutil.rmtree(dest)
                    else:
                        os.remove(dest)

                if os.path.isdir(src):
                    shutil.copytree(src, dest)
                else:
                    shutil.copy2(src, dest)

            print("✅ Backup restored successfully.")
            return True
        except Exception as e:
            print(f"❌ Error restoring backup: {e}")
            return False

    def save_version(self, version):
        """Save current version to file."""
        version_data = {"version": version, "updated": str(os.path.getctime(__file__))}

        version_path = os.path.join(self.script_dir, VERSION_FILE)
        with open(version_path, "w") as f:
            json.dump(version_data, f, indent=2)


def main():
    """Main update function."""
    print("🎮 SS6 Super Student Game - Auto Updater")
    print("=" * 50)

    updater = GameUpdater()

    # Check for updates
    update_info = updater.check_for_updates()

    if update_info.get("available"):
        print(f"\n🆕 Update available: v{update_info['version']}")
        print("\n📋 What's new:")
        print(update_info.get("release_notes", "No release notes available.")[:500])

        # Ask user if they want to update
        response = (
            input("\n❓ Do you want to download and install this update? (y/n): ").lower().strip()
        )

        if response in ["y", "yes"]:
            success = updater.download_update(update_info)
            if success:
                print("\n🎉 Update completed successfully!")
                print("🚀 You can now restart the game to use the new version.")

                # Ask if user wants to start the game
                start_game = input("\n❓ Start the game now? (y/n): ").lower().strip()
                if start_game in ["y", "yes"]:
                    try:
                        if os.path.exists("SS6.origional.py"):
                            subprocess.Popen([sys.executable, "SS6.origional.py"])
                        elif os.path.exists("SuperStudent.exe"):
                            subprocess.Popen(["SuperStudent.exe"])
                        else:
                            print("❌ Could not find game executable.")
                    except Exception as e:
                        print(f"❌ Error starting game: {e}")
            else:
                print("\n❌ Update failed. Please try again later.")
        else:
            print("⏭️  Update skipped. You can run this script again anytime.")

    elif "error" in update_info:
        print(f"\n⚠️  Could not check for updates: {update_info['error']}")
        print("🌐 Please check your internet connection and try again.")

    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()
