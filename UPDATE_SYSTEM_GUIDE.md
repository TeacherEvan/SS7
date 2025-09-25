# SS6 Game Update System

## 🎯 **Automatic Updates via GitHub**

The SS6 Super Student Game now includes an automatic update system that connects to GitHub to download and install the latest versions.

### 🚀 **How to Update**

#### Option 1: Easy Update (Windows)

1. Double-click `Update_Game.bat`
2. Follow the on-screen prompts
3. Updates download and install automatically

#### Option 2: Manual Update (All Platforms)

1. Open terminal/command prompt in game directory
2. Run: `python update_game.py`
3. Follow the interactive prompts

### ✨ **Features**

- ✅ **Automatic Version Detection** - Compares local vs GitHub versions
- ✅ **Safe Backup System** - Creates backup before updating
- ✅ **Rollback Protection** - Restores backup if update fails
- ✅ **Release Notes** - Shows what's new in each update
- ✅ **Network Error Handling** - Graceful failure with helpful messages
- ✅ **Cross-Platform** - Works on Windows, Linux, and macOS

### 🔧 **Technical Details**

**Update Source**: GitHub Releases at `https://github.com/TeacherEvan/SS7/releases`
**Version Tracking**: `version.json` file in game directory
**Backup Location**: `backup/` folder (created automatically)
**Network Requirements**: Internet connection for checking/downloading updates

### 📋 **Update Process**

1. **Version Check** - Contacts GitHub API to check latest release
2. **Comparison** - Compares local version with GitHub version  
3. **User Prompt** - Asks permission before downloading
4. **Backup Creation** - Safely backs up current game files
5. **Download** - Downloads latest release package from GitHub
6. **Installation** - Extracts and replaces game files
7. **Verification** - Updates version tracking and confirms success

### 🛡️ **Safety Features**

- **Automatic Backup** - Always creates backup before updating
- **Rollback on Failure** - Restores backup if anything goes wrong
- **Version Verification** - Confirms successful update completion
- **Error Handling** - Provides clear error messages and recovery options

### 🌐 **Network Requirements**

- **Internet Connection** - Required only during update check/download
- **GitHub Access** - Must be able to reach api.github.com and github.com
- **Firewall** - May need to allow Python/updater through firewall

### 📱 **For Classroom Deployment**

The update system is designed to work in educational environments:

- **No Installation Required** - Updates existing portable installation
- **Backup Safety** - Never loses working game version
- **Offline Operation** - Game works normally without internet
- **Update on Demand** - Only checks for updates when requested
- **Teacher Friendly** - Simple double-click operation

### 🔄 **Update Frequency**

- **Manual Only** - Updates never happen automatically
- **On-Demand** - Run update checker when convenient
- **Version Tracking** - Always shows current vs available versions
- **Release Notes** - See what's new before updating

### ❓ **Troubleshooting**

**"No internet connection"**

- Check network connectivity
- Verify firewall settings
- Try again later

**"Update failed"**

- Game automatically restores from backup
- No loss of functionality
- Can retry update process

**"Cannot find update file"**

- Ensure `update_game.py` is in game directory
- Re-download game if missing files

### 📞 **Support**

For update issues or questions:

- Check GitHub repository issues page
- Verify system requirements are met  
- Ensure stable internet connection during updates

---

**Current Version**: 1.1.0 (includes complete emoji learning system)
**Last Updated**: January 21, 2025
