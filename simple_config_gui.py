"""
Simple Configuration GUI for SS6 Super Student Game.
NO user profiles, NO difficulty settings, NO complex customization.
Just basic game settings that teachers might want to adjust.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import yaml
import os
from pathlib import Path

class SimpleConfigGUI:
    """
    Simple GUI for basic SS6 game settings only.
    """
    
    def __init__(self):
        """Initialize the simple configuration GUI."""
        self.root = tk.Tk()
        self.root.title("SS6 Super Student - Game Settings")
        self.root.geometry("400x350")
        self.root.resizable(False, False)
        
        # Load current configuration
        self.config_dir = Path(__file__).parent / "config"
        self.config = self.load_config()
        
        # Setup the simple GUI
        self.setup_gui()
        
    def load_config(self):
        """Load simple configuration from YAML file."""
        config_file = self.config_dir / "teacher_config.yaml"
        try:
            with open(config_file, 'r') as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            return self.get_default_config()
    
    def get_default_config(self):
        """Get default simple configuration."""
        return {
            'display': {
                'mode': 'DEFAULT',
                'fullscreen': False
            },
            'audio': {
                'sound_effects': True,
                'background_music': True,
                'voice_announcements': True
            },
            'game_modes': {
                'enabled': ['alphabet', 'numbers', 'shapes', 'colors']
            },
            'visual': {
                'show_explosions': True,
                'show_particles': True
            }
        }
    
    def setup_gui(self):
        """Setup the simple GUI components."""
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title = ttk.Label(main_frame, text="SS6 Game Settings", 
                         font=('Arial', 16, 'bold'))
        title.pack(pady=(0, 20))
        
        # Display Settings
        display_frame = ttk.LabelFrame(main_frame, text="Display", padding=10)
        display_frame.pack(fill='x', pady=5)
        
        self.fullscreen_var = tk.BooleanVar(
            value=self.config.get('display', {}).get('fullscreen', False)
        )
        ttk.Checkbutton(display_frame, text="Fullscreen Mode", 
                       variable=self.fullscreen_var).pack(anchor='w')
        
        # Audio Settings
        audio_frame = ttk.LabelFrame(main_frame, text="Audio", padding=10)
        audio_frame.pack(fill='x', pady=5)
        
        audio_config = self.config.get('audio', {})
        
        self.sound_effects_var = tk.BooleanVar(
            value=audio_config.get('sound_effects', True)
        )
        ttk.Checkbutton(audio_frame, text="Sound Effects", 
                       variable=self.sound_effects_var).pack(anchor='w')
        
        self.background_music_var = tk.BooleanVar(
            value=audio_config.get('background_music', True)
        )
        ttk.Checkbutton(audio_frame, text="Background Music", 
                       variable=self.background_music_var).pack(anchor='w')
        
        self.voice_var = tk.BooleanVar(
            value=audio_config.get('voice_announcements', True)
        )
        ttk.Checkbutton(audio_frame, text="Voice Announcements", 
                       variable=self.voice_var).pack(anchor='w')
        
        # Game Modes
        modes_frame = ttk.LabelFrame(main_frame, text="Game Modes", padding=10)
        modes_frame.pack(fill='x', pady=5)
        
        self.game_mode_vars = {}
        enabled_modes = self.config.get('game_modes', {}).get('enabled', [])
        
        for mode in ['alphabet', 'numbers', 'shapes', 'colors']:
            var = tk.BooleanVar(value=mode in enabled_modes)
            self.game_mode_vars[mode] = var
            ttk.Checkbutton(modes_frame, text=mode.title(), 
                           variable=var).pack(anchor='w')
        
        # Visual Effects
        visual_frame = ttk.LabelFrame(main_frame, text="Visual Effects", padding=10)
        visual_frame.pack(fill='x', pady=5)
        
        visual_config = self.config.get('visual', {})
        
        self.explosions_var = tk.BooleanVar(
            value=visual_config.get('show_explosions', True)
        )
        ttk.Checkbutton(visual_frame, text="Show Explosions", 
                       variable=self.explosions_var).pack(anchor='w')
        
        self.particles_var = tk.BooleanVar(
            value=visual_config.get('show_particles', True)
        )
        ttk.Checkbutton(visual_frame, text="Show Particle Effects", 
                       variable=self.particles_var).pack(anchor='w')
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=15)
        
        ttk.Button(button_frame, text="Save Settings", 
                  command=self.save_config).pack(side='right', padx=5)
        ttk.Button(button_frame, text="Cancel", 
                  command=self.root.quit).pack(side='right', padx=5)
        ttk.Button(button_frame, text="Reset", 
                  command=self.reset_to_defaults).pack(side='left', padx=5)
    
    def save_config(self):
        """Save the configuration to file."""
        try:
            # Update config with current values
            self.config['display'] = {
                'mode': 'DEFAULT',
                'fullscreen': self.fullscreen_var.get()
            }
            
            self.config['audio'] = {
                'sound_effects': self.sound_effects_var.get(),
                'background_music': self.background_music_var.get(),
                'voice_announcements': self.voice_var.get()
            }
            
            self.config['game_modes'] = {
                'enabled': [mode for mode, var in self.game_mode_vars.items() if var.get()]
            }
            
            self.config['visual'] = {
                'show_explosions': self.explosions_var.get(),
                'show_particles': self.particles_var.get()
            }
            
            # Save to file
            os.makedirs(self.config_dir, exist_ok=True)
            with open(self.config_dir / "teacher_config.yaml", 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)
            
            messagebox.showinfo("Success", "Settings saved successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")
    
    def reset_to_defaults(self):
        """Reset configuration to defaults."""
        if messagebox.askyesno("Reset Settings", "Reset all settings to defaults?"):
            self.config = self.get_default_config()
            self.root.destroy()
            self.__init__()  # Reinitialize with defaults
    
    def run(self):
        """Run the GUI."""
        self.root.mainloop()

def main():
    """Main function to run the simple configuration GUI."""
    app = SimpleConfigGUI()
    app.run()

if __name__ == "__main__":
    main()