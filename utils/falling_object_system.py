"""
Falling Object System for SS6 Game

This module provides a common physics and rendering system for falling objects
across all game levels, reducing duplicate code and improving performance.
"""

import random
import pygame
from typing import List, Dict, Any, Tuple, Optional


class FallingObject:
    """Represents a single falling object with physics and rendering properties."""
    
    def __init__(self, value: str, x: int, y: int, size: int = 240, 
                 object_type: str = "letter", **kwargs):
        """
        Initialize a falling object.
        
        Args:
            value: The value/content of the object (letter, number, etc.)
            x: Initial X position
            y: Initial Y position  
            size: Size of the object
            object_type: Type of object ("letter", "number", "emoji", etc.)
            **kwargs: Additional properties
        """
        self.value = value
        self.x = float(x)
        self.y = float(y)
        self.size = size
        self.object_type = object_type
        
        # Physics properties
        self.dx = kwargs.get('dx', random.choice([-1, -0.5, 0.5, 1]) * 1.5)
        self.dy = kwargs.get('dy', random.choice([5, 10.5]) * 1.5 * 1.2)
        self.mass = kwargs.get('mass', random.uniform(40, 60))
        self.can_bounce = kwargs.get('can_bounce', False)
        
        # Rendering properties
        self.rect = pygame.Rect(int(x), int(y), size, size)
        self.surface = kwargs.get('surface', None)
        self.color = kwargs.get('color', (0, 0, 0))
        
        # State
        self.alive = True
        self.hit = kwargs.get('hit', False)
        self.off_screen = False


class FallingObjectSystem:
    """
    Manages physics, collision detection, and rendering for falling objects.
    Reduces code duplication across different game levels.
    """
    
    def __init__(self, width: int, height: int, spawn_interval: int = 60):
        """
        Initialize the falling object system.
        
        Args:
            width: Screen width
            height: Screen height  
            spawn_interval: Frames between spawns
        """
        self.width = width
        self.height = height
        self.spawn_interval = spawn_interval
        
        self.objects: List[FallingObject] = []
        self.frame_count = 0
        self.spawn_queue: List[str] = []
        
        # Performance settings
        self.max_objects = 50  # Limit active objects for performance
        self.collision_frequency = 1  # Check collisions every N frames

    def set_spawn_queue(self, items: List[str]):
        """Set the queue of items to spawn."""
        self.spawn_queue = items.copy()

    def update(self):
        """Update all falling objects physics and remove off-screen objects."""
        self.frame_count += 1
        
        # Spawn new objects
        self._spawn_objects()
        
        # Update existing objects
        active_objects = []
        for obj in self.objects:
            if self._update_object(obj):
                active_objects.append(obj)
        
        self.objects = active_objects

    def _spawn_objects(self):
        """Spawn new objects based on spawn interval and queue."""
        if (self.spawn_queue and 
            len(self.objects) < self.max_objects and
            self.frame_count % self.spawn_interval == 0):
            
            value = self.spawn_queue.pop(0)
            obj = FallingObject(
                value=value,
                x=random.randint(50, self.width - 50),
                y=-50,
                size=240
            )
            self.objects.append(obj)

    def _update_object(self, obj: FallingObject) -> bool:
        """
        Update a single object's physics.
        
        Args:
            obj: The object to update
            
        Returns:
            bool: True if object should remain active, False if should be removed
        """
        if not obj.alive:
            return False
            
        # Update position
        obj.x += obj.dx
        obj.y += obj.dy
        
        # Update rect for collision detection
        obj.rect.center = (int(obj.x), int(obj.y))
        
        # Check if off-screen
        if obj.y > self.height + 100:
            obj.off_screen = True
            return False
            
        # Horizontal boundary bouncing
        if obj.x <= 50 or obj.x >= self.width - 50:
            if obj.can_bounce:
                obj.dx *= -0.8  # Bounce with energy loss
            else:
                obj.dx *= -1  # Simple reflection
                
        return True

    def check_collisions(self, click_x: int, click_y: int, 
                        target_value: Optional[str] = None) -> List[FallingObject]:
        """
        Check for collisions with falling objects.
        
        Args:
            click_x: X coordinate of click/touch
            click_y: Y coordinate of click/touch
            target_value: Optional target value to filter collisions
            
        Returns:
            List of objects that were hit
        """
        hit_objects = []
        click_point = pygame.math.Vector2(click_x, click_y)
        
        for obj in self.objects:
            if not obj.alive:
                continue
                
            # Check distance collision (more forgiving than rect collision)
            obj_center = pygame.math.Vector2(obj.x, obj.y)
            distance = click_point.distance_to(obj_center)
            
            if distance <= obj.size // 2:  # Hit if within object radius
                # If target filtering is enabled, only hit target objects
                if target_value is None or obj.value == target_value:
                    obj.hit = True
                    hit_objects.append(obj)
                    
        return hit_objects

    def remove_hit_objects(self) -> int:
        """Remove all hit objects and return count removed."""
        removed_count = 0
        active_objects = []
        
        for obj in self.objects:
            if obj.hit:
                removed_count += 1
                obj.alive = False
            else:
                active_objects.append(obj)
                
        self.objects = active_objects
        return removed_count

    def render(self, screen: pygame.Surface, font: pygame.font.Font, 
               target_value: Optional[str] = None, 
               resource_manager=None, mode: str = "alphabet"):
        """
        Render all falling objects.
        
        Args:
            screen: Pygame screen surface
            font: Font to use for rendering text
            target_value: Current target value for highlighting
            resource_manager: Optional resource manager for cached surfaces
            mode: Game mode for rendering context
        """
        for obj in self.objects:
            if not obj.alive:
                continue
                
            # Determine colors
            is_target = (target_value is not None and obj.value == target_value)
            text_color = (0, 0, 0) if is_target else (150, 150, 150)
            
            # Use cached surface if available
            if resource_manager and obj.object_type in ['letter', 'number']:
                try:
                    cached_surface = resource_manager.get_falling_object_surface(
                        mode, obj.value, text_color
                    )
                    if cached_surface:
                        text_rect = cached_surface.get_rect(center=(int(obj.x), int(obj.y)))
                        screen.blit(cached_surface, text_rect)
                        continue
                except:
                    pass  # Fall back to direct rendering
            
            # Use pre-rendered surface if available (for emojis)
            if obj.surface:
                surface_rect = obj.surface.get_rect(center=(int(obj.x), int(obj.y)))
                screen.blit(obj.surface, surface_rect)
            else:
                # Fallback: Direct text rendering
                display_value = obj.value
                if mode == "clcase" and obj.value == "a":
                    display_value = "α"
                    
                text_surface = font.render(display_value, True, text_color)
                text_rect = text_surface.get_rect(center=(int(obj.x), int(obj.y)))
                screen.blit(text_surface, text_rect)

    def get_active_count(self) -> int:
        """Get the number of active objects."""
        return len([obj for obj in self.objects if obj.alive])

    def get_objects_by_value(self, value: str) -> List[FallingObject]:
        """Get all active objects with a specific value."""
        return [obj for obj in self.objects if obj.alive and obj.value == value]

    def clear_all(self):
        """Clear all objects."""
        self.objects.clear()
        self.spawn_queue.clear()
        self.frame_count = 0

    def apply_explosion_effect(self, explosion_x: int, explosion_y: int, 
                             max_radius: int = 200):
        """Apply explosion push effect to nearby objects."""
        explosion_center = pygame.math.Vector2(explosion_x, explosion_y)
        
        for obj in self.objects:
            if not obj.alive:
                continue
                
            obj_center = pygame.math.Vector2(obj.x, obj.y)
            distance = explosion_center.distance_to(obj_center)
            
            if distance < max_radius and distance > 0:
                # Calculate push force (stronger when closer)
                force_magnitude = (max_radius - distance) / max_radius * 15
                
                # Calculate push direction
                direction = (obj_center - explosion_center).normalize()
                
                # Apply push to object velocity
                obj.dx += direction.x * force_magnitude
                obj.dy += direction.y * force_magnitude
                
                # Enable bouncing after explosion
                obj.can_bounce = True