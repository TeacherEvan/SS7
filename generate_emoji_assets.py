"""
Emoji Asset Generator for SS6 Super Student Game
Creates placeholder emoji PNG files for the alphabet level.
"""

import pygame
import os
from pathlib import Path

# Initialize pygame for font rendering
pygame.init()

# Emoji associations as defined in the instructions
EMOJI_ASSOCIATIONS = {
    'A': ['Apple', 'Ant'],
    'B': ['Ball', 'Banana'],
    'C': ['Cat', 'Car'],
    'D': ['Dog', 'Duck'],
    'E': ['Elephant', 'Egg'],
    'F': ['Fish', 'Flower'],
    'G': ['Giraffe', 'Grapes'],
    'H': ['House', 'Hat'],
    'I': ['Ice Cream', 'Iguana'],
    'J': ['Jar', 'Juice'],
    'K': ['Kite', 'Key'],
    'L': ['Lion', 'Leaf'],
    'M': ['Mouse', 'Moon'],
    'N': ['Nest', 'Nose'],
    'O': ['Orange', 'Owl'],
    'P': ['Penguin', 'Pizza'],
    'Q': ['Queen', 'Question Mark'],
    'R': ['Rainbow', 'Rabbit'],
    'S': ['Sun', 'Snake'],
    'T': ['Tree', 'Tiger'],
    'U': ['Umbrella', 'Unicorn'],
    'V': ['Violin', 'Volcano'],
    'W': ['Whale', 'Watermelon'],
    'X': ['X-ray', 'Xylophone'],
    'Y': ['Yarn', 'Yacht'],
    'Z': ['Zebra', 'Zipper']
}

def create_placeholder_emoji(emoji_name, size=(128, 128)):
    """Create a placeholder emoji image with text."""
    # Create surface
    surface = pygame.Surface(size, pygame.SRCALPHA)
    surface.fill((255, 255, 255, 0))  # Transparent background
    
    # Create colorful background circle
    center = (size[0] // 2, size[1] // 2)
    radius = min(size) // 2 - 5
    
    # Different colors for different emojis
    colors = [
        (255, 200, 200),  # Light red
        (200, 255, 200),  # Light green
        (200, 200, 255),  # Light blue
        (255, 255, 200),  # Light yellow
        (255, 200, 255),  # Light magenta
        (200, 255, 255),  # Light cyan
    ]
    
    color = colors[hash(emoji_name) % len(colors)]
    pygame.draw.circle(surface, color, center, radius)
    pygame.draw.circle(surface, (100, 100, 100), center, radius, 2)
    
    # Add text
    font_size = min(20, size[0] // 6)
    font = pygame.font.Font(None, font_size)
    
    # Split text into multiple lines if too long
    words = emoji_name.split(' ')
    lines = []
    current_line = ""
    
    for word in words:
        test_line = current_line + (" " if current_line else "") + word
        if font.size(test_line)[0] <= size[0] - 20:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    
    if current_line:
        lines.append(current_line)
    
    # Render text lines
    total_height = len(lines) * font_size
    start_y = center[1] - total_height // 2
    
    for i, line in enumerate(lines):
        text_surface = font.render(line, True, (50, 50, 50))
        text_rect = text_surface.get_rect(center=(center[0], start_y + i * font_size))
        surface.blit(text_surface, text_rect)
    
    return surface

def generate_emoji_assets():
    """Generate all emoji assets for the alphabet."""
    assets_dir = Path("assets/emojis")
    assets_dir.mkdir(parents=True, exist_ok=True)
    
    print("Generating emoji placeholder assets...")
    
    for letter, emojis in EMOJI_ASSOCIATIONS.items():
        for i, emoji_name in enumerate(emojis, 1):
            # Create filename
            filename = f"{letter}_{emoji_name.lower().replace(' ', '_')}_{i}.png"
            filepath = assets_dir / filename
            
            # Generate placeholder image
            emoji_surface = create_placeholder_emoji(emoji_name, (128, 128))
            
            # Save as PNG
            pygame.image.save(emoji_surface, str(filepath))
            print(f"Created: {filename}")
    
    print(f"Generated {sum(len(emojis) for emojis in EMOJI_ASSOCIATIONS.values())} emoji placeholder files")

if __name__ == "__main__":
    generate_emoji_assets()
    pygame.quit()