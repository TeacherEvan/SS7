"""
Texture Atlas System for SS6 Super Student Game
Combines multiple textures into single surfaces for faster rendering.
"""

import pygame
from typing import Dict, List, Tuple, Optional
import json
import os
from pathlib import Path

class TextureAtlas:
    """
    Texture atlas for combining multiple small textures into one large texture.
    """
    
    def __init__(self, width: int = 1024, height: int = 1024):
        """
        Initialize texture atlas.
        
        Args:
            width: Atlas width in pixels
            height: Atlas height in pixels
        """
        self.width = width
        self.height = height
        self.surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self.surface = self.surface.convert_alpha()
        
        self.regions: Dict[str, pygame.Rect] = {}
        self.current_x = 0
        self.current_y = 0
        self.row_height = 0
    
    def add_texture(self, name: str, texture: pygame.Surface) -> bool:
        """
        Add a texture to the atlas.
        
        Args:
            name: Unique name for the texture
            texture: Pygame surface to add
            
        Returns:
            True if texture was added successfully, False if no space
        """
        tex_width = texture.get_width()
        tex_height = texture.get_height()
        
        # Check if texture fits in current row
        if self.current_x + tex_width > self.width:
            # Move to next row
            self.current_x = 0
            self.current_y += self.row_height
            self.row_height = 0
        
        # Check if texture fits in atlas at all
        if (self.current_x + tex_width > self.width or 
            self.current_y + tex_height > self.height):
            return False
        
        # Add texture to atlas
        rect = pygame.Rect(self.current_x, self.current_y, tex_width, tex_height)
        self.surface.blit(texture, rect)
        self.regions[name] = rect
        
        # Update position tracking
        self.current_x += tex_width
        self.row_height = max(self.row_height, tex_height)
        
        return True
    
    def get_texture_rect(self, name: str) -> Optional[pygame.Rect]:
        """Get the rectangle for a named texture in the atlas."""
        return self.regions.get(name)
    
    def get_subsurface(self, name: str) -> Optional[pygame.Surface]:
        """Get a subsurface for a named texture."""
        rect = self.regions.get(name)
        if rect:
            return self.surface.subsurface(rect)
        return None
    
    def save_atlas(self, image_path: str, data_path: str):
        """
        Save atlas image and metadata.
        
        Args:
            image_path: Path to save atlas image
            data_path: Path to save atlas metadata JSON
        """
        # Save image
        pygame.image.save(self.surface, image_path)
        
        # Save metadata
        metadata = {
            'width': self.width,
            'height': self.height,
            'regions': {name: [rect.x, rect.y, rect.width, rect.height] 
                       for name, rect in self.regions.items()}
        }
        
        with open(data_path, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def load_atlas(self, image_path: str, data_path: str) -> bool:
        """
        Load atlas from saved files.
        
        Args:
            image_path: Path to atlas image
            data_path: Path to atlas metadata JSON
            
        Returns:
            True if loaded successfully
        """
        try:
            # Load image
            self.surface = pygame.image.load(image_path).convert_alpha()
            
            # Load metadata
            with open(data_path, 'r') as f:
                metadata = json.load(f)
            
            self.width = metadata['width']
            self.height = metadata['height']
            
            # Reconstruct regions
            self.regions = {}
            for name, rect_data in metadata['regions'].items():
                self.regions[name] = pygame.Rect(*rect_data)
            
            return True
        
        except Exception as e:
            print(f"Failed to load atlas: {e}")
            return False

class AtlasManager:
    """
    Manages multiple texture atlases for the game.
    """
    
    def __init__(self):
        self.atlases: Dict[str, TextureAtlas] = {}
        self.texture_cache: Dict[str, pygame.Surface] = {}
    
    def create_atlas(self, name: str, width: int = 1024, height: int = 1024) -> TextureAtlas:
        """Create a new texture atlas."""
        atlas = TextureAtlas(width, height)
        self.atlases[name] = atlas
        return atlas
    
    def get_atlas(self, name: str) -> Optional[TextureAtlas]:
        """Get an atlas by name."""
        return self.atlases.get(name)
    
    def build_ui_atlas(self, font_sizes: Dict[str, int], display_mode: str = 'DEFAULT'):
        """
        Build texture atlas for UI elements and text.
        
        Args:
            font_sizes: Dictionary of font size configurations
            display_mode: Display mode for sizing
        """
        atlas = self.create_atlas('ui', 2048, 2048)
        
        # Load fonts
        fonts = {}
        base_font_size = font_sizes.get(display_mode, {}).get('base', 24)
        
        try:
            fonts['small'] = pygame.font.Font(None, base_font_size)
            fonts['medium'] = pygame.font.Font(None, int(base_font_size * 1.5))
            fonts['large'] = pygame.font.Font(None, int(base_font_size * 2))
        except:
            # Fallback to default font
            fonts['small'] = pygame.font.Font(None, 24)
            fonts['medium'] = pygame.font.Font(None, 36)
            fonts['large'] = pygame.font.Font(None, 48)
        
        # Common UI text elements
        ui_texts = [
            'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
            'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
            '1', '2', '3', '4', '5', '6', '7', '8', '9', '10',
            'Circle', 'Square', 'Triangle', 'Rectangle', 'Pentagon',
            'Red', 'Blue', 'Green', 'Yellow', 'Purple'
        ]
        
        colors = [
            (255, 255, 255),  # White
            (255, 255, 0),    # Yellow
            (255, 100, 100),  # Light red
            (100, 255, 100),  # Light green
            (100, 100, 255),  # Light blue
        ]
        
        # Generate text textures
        for font_name, font in fonts.items():
            for text in ui_texts:
                for i, color in enumerate(colors):
                    try:
                        text_surface = font.render(text, True, color)
                        texture_name = f"{font_name}_{text}_{i}"
                        
                        if not atlas.add_texture(texture_name, text_surface):
                            print(f"Warning: Could not add texture {texture_name} to UI atlas")
                    
                    except Exception as e:
                        print(f"Error creating text texture for '{text}': {e}")
        
        # Cache atlas surface
        self.texture_cache['ui_atlas'] = atlas.surface
        
        return atlas
    
    def build_particle_atlas(self):
        """Build texture atlas for particle effects."""
        atlas = self.create_atlas('particles', 512, 512)
        
        # Generate particle textures
        particle_sizes = [4, 8, 12, 16, 20]
        particle_colors = [
            (255, 100, 100),  # Red
            (100, 255, 100),  # Green  
            (100, 100, 255),  # Blue
            (255, 255, 100),  # Yellow
            (255, 100, 255),  # Magenta
            (100, 255, 255),  # Cyan
            (255, 255, 255),  # White
        ]
        
        for size in particle_sizes:
            for i, color in enumerate(particle_colors):
                # Create circular particle
                particle_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(particle_surf, color, (size, size), size)
                
                # Add gradient effect
                for r in range(size, 0, -1):
                    alpha = int(255 * (r / size) * 0.8)
                    gradient_color = (*color, alpha)
                    gradient_surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
                    pygame.draw.circle(gradient_surf, gradient_color, (r, r), r)
                    particle_surf.blit(gradient_surf, (size - r, size - r), special_flags=pygame.BLEND_ALPHA_SDL2)
                
                texture_name = f"particle_{size}_{i}"
                if not atlas.add_texture(texture_name, particle_surf):
                    print(f"Warning: Could not add particle texture {texture_name}")
        
        # Cache atlas surface
        self.texture_cache['particle_atlas'] = atlas.surface
        
        return atlas
    
    def get_texture(self, atlas_name: str, texture_name: str) -> Optional[pygame.Surface]:
        """Get a texture from an atlas."""
        atlas = self.atlases.get(atlas_name)
        if atlas:
            return atlas.get_subsurface(texture_name)
        return None
    
    def save_all_atlases(self, base_path: str):
        """Save all atlases to disk."""
        base_path = Path(base_path)
        base_path.mkdir(exist_ok=True)
        
        for name, atlas in self.atlases.items():
            image_path = base_path / f"{name}_atlas.png"
            data_path = base_path / f"{name}_atlas.json"
            atlas.save_atlas(str(image_path), str(data_path))
    
    def load_all_atlases(self, base_path: str):
        """Load all atlases from disk."""
        base_path = Path(base_path)
        
        if not base_path.exists():
            return
        
        # Find all atlas files
        atlas_files = list(base_path.glob("*_atlas.png"))
        
        for image_path in atlas_files:
            atlas_name = image_path.stem.replace('_atlas', '')
            data_path = base_path / f"{atlas_name}_atlas.json"
            
            if data_path.exists():
                atlas = TextureAtlas()
                if atlas.load_atlas(str(image_path), str(data_path)):
                    self.atlases[atlas_name] = atlas
                    self.texture_cache[f"{atlas_name}_atlas"] = atlas.surface

# Global atlas manager instance
atlas_manager = AtlasManager()

def get_atlas_manager() -> AtlasManager:
    """Get the global atlas manager instance."""
    return atlas_manager