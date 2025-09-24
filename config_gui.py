"""
Simple Configuration GUI for SS6 Super Student Game.
NO user profiles, NO difficulty settings, NO complex customization.
Redirects to the simple configuration interface.
"""

def main():
    """Main function to run the simple configuration GUI."""
    try:
        from simple_config_gui import SimpleConfigGUI
        app = SimpleConfigGUI()
        app.run()
    except ImportError:
        print("Error: simple_config_gui.py not found")
    except Exception as e:
        print(f"Error starting configuration GUI: {e}")

if __name__ == "__main__":
    main()