"""
Object Pool System for SS6 Super Student Game
Improves performance by reusing objects instead of constantly creating/destroying them.
"""

from typing import Dict, List, TypeVar, Generic, Callable, Any
import pygame
from collections import deque

T = TypeVar('T')

class ObjectPool(Generic[T]):
    """
    Generic object pool for reusing objects to improve performance.
    """
    
    def __init__(self, factory: Callable[[], T], reset_func: Callable[[T], None] = None, 
                 initial_size: int = 10, max_size: int = 100):
        """
        Initialize object pool.
        
        Args:
            factory: Function to create new objects
            reset_func: Function to reset objects when returned to pool
            initial_size: Initial number of objects to create
            max_size: Maximum pool size
        """
        self.factory = factory
        self.reset_func = reset_func
        self.max_size = max_size
        self.available = deque()
        self.in_use = set()
        
        # Pre-populate the pool
        for _ in range(initial_size):
            obj = self.factory()
            self.available.append(obj)
    
    def get(self) -> T:
        """Get an object from the pool."""
        if self.available:
            obj = self.available.popleft()
        else:
            obj = self.factory()
        
        self.in_use.add(obj)
        return obj
    
    def return_object(self, obj: T):
        """Return an object to the pool."""
        if obj in self.in_use:
            self.in_use.remove(obj)
            
            # Reset the object if reset function provided
            if self.reset_func:
                self.reset_func(obj)
            
            # Only keep up to max_size objects in pool
            if len(self.available) < self.max_size:
                self.available.append(obj)
    
    def clear(self):
        """Clear all objects from the pool."""
        self.available.clear()
        self.in_use.clear()
    
    def get_stats(self) -> Dict[str, int]:
        """Get pool statistics."""
        return {
            'available': len(self.available),
            'in_use': len(self.in_use),
            'total': len(self.available) + len(self.in_use)
        }

class Particle:
    """Particle object for pooling."""
    
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self.life = 1.0
        self.max_life = 1.0
        self.color = (255, 255, 255)
        self.size = 3
        self.active = False
    
    def reset(self):
        """Reset particle to default state."""
        self.x = 0.0
        self.y = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self.life = 1.0
        self.max_life = 1.0
        self.color = (255, 255, 255)
        self.size = 3
        self.active = False
    
    def update(self, dt: float):
        """Update particle state."""
        if not self.active:
            return False
        
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt
        
        if self.life <= 0:
            self.active = False
            return False
        
        return True
    
    def draw(self, screen: pygame.Surface):
        """Draw the particle."""
        if not self.active:
            return
        
        alpha = int(255 * (self.life / self.max_life))
        color_with_alpha = (*self.color, alpha)
        
        # Create a surface for the particle with per-pixel alpha
        particle_surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(particle_surf, color_with_alpha, (self.size, self.size), self.size)
        
        screen.blit(particle_surf, (int(self.x - self.size), int(self.y - self.size)))

class Explosion:
    """Explosion object for pooling."""
    
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.scale = 1.0
        self.life = 1.0
        self.max_life = 1.0
        self.color = (255, 100, 0)
        self.active = False
        self.particles = []
    
    def reset(self):
        """Reset explosion to default state."""
        self.x = 0.0
        self.y = 0.0
        self.scale = 1.0
        self.life = 1.0
        self.max_life = 1.0
        self.color = (255, 100, 0)
        self.active = False
        self.particles.clear()
    
    def initialize(self, x: float, y: float, particle_count: int = 20):
        """Initialize explosion at position."""
        self.x = x
        self.y = y
        self.life = 1.0
        self.max_life = 1.0
        self.active = True
        
        # Create explosion particles (these could also be pooled)
        import random
        import math
        
        self.particles.clear()
        for _ in range(particle_count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(50, 200)
            self.particles.append({
                'x': x,
                'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'life': random.uniform(0.5, 1.5),
                'max_life': random.uniform(0.5, 1.5),
                'size': random.randint(2, 6),
                'color': (
                    random.randint(200, 255),
                    random.randint(50, 150),
                    random.randint(0, 50)
                )
            })
    
    def update(self, dt: float):
        """Update explosion state."""
        if not self.active:
            return False
        
        self.life -= dt
        self.scale = 1.0 + (1.0 - self.life / self.max_life) * 2.0
        
        # Update particles
        active_particles = []
        for particle in self.particles:
            particle['x'] += particle['vx'] * dt
            particle['y'] += particle['vy'] * dt
            particle['life'] -= dt
            
            if particle['life'] > 0:
                active_particles.append(particle)
        
        self.particles = active_particles
        
        if self.life <= 0 and not self.particles:
            self.active = False
            return False
        
        return True
    
    def draw(self, screen: pygame.Surface):
        """Draw the explosion."""
        if not self.active:
            return
        
        for particle in self.particles:
            if particle['life'] > 0:
                alpha = int(255 * (particle['life'] / particle['max_life']))
                color_with_alpha = (*particle['color'], alpha)
                
                # Create a surface for the particle with per-pixel alpha
                size = int(particle['size'] * self.scale)
                if size > 0:
                    particle_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                    pygame.draw.circle(particle_surf, color_with_alpha, (size, size), size)
                    screen.blit(particle_surf, (int(particle['x'] - size), int(particle['y'] - size)))

class PoolManager:
    """
    Manages all object pools for the game.
    """
    
    def __init__(self):
        """Initialize pool manager with common pools."""
        self.pools: Dict[str, ObjectPool] = {}
        
        # Create common pools
        self.create_particle_pool()
        self.create_explosion_pool()
    
    def create_particle_pool(self, initial_size: int = 50, max_size: int = 200):
        """Create particle object pool."""
        self.pools['particles'] = ObjectPool(
            factory=lambda: Particle(),
            reset_func=lambda p: p.reset(),
            initial_size=initial_size,
            max_size=max_size
        )
    
    def create_explosion_pool(self, initial_size: int = 10, max_size: int = 30):
        """Create explosion object pool."""
        self.pools['explosions'] = ObjectPool(
            factory=lambda: Explosion(),
            reset_func=lambda e: e.reset(),
            initial_size=initial_size,
            max_size=max_size
        )
    
    def get_particle(self) -> Particle:
        """Get a particle from the pool."""
        return self.pools['particles'].get()
    
    def return_particle(self, particle: Particle):
        """Return a particle to the pool."""
        self.pools['particles'].return_object(particle)
    
    def get_explosion(self) -> Explosion:
        """Get an explosion from the pool."""
        return self.pools['explosions'].get()
    
    def return_explosion(self, explosion: Explosion):
        """Return an explosion to the pool."""
        self.pools['explosions'].return_object(explosion)
    
    def get_pool_stats(self) -> Dict[str, Dict[str, int]]:
        """Get statistics for all pools."""
        return {name: pool.get_stats() for name, pool in self.pools.items()}
    
    def clear_all_pools(self):
        """Clear all object pools."""
        for pool in self.pools.values():
            pool.clear()

class SpriteGroup:
    """
    Optimized sprite group for batch rendering.
    """
    
    def __init__(self):
        self.sprites = []
        self.dirty_sprites = set()
        self.background = None
        self.rect = None
    
    def add(self, sprite):
        """Add sprite to group."""
        if sprite not in self.sprites:
            self.sprites.append(sprite)
            self.dirty_sprites.add(sprite)
    
    def remove(self, sprite):
        """Remove sprite from group."""
        if sprite in self.sprites:
            self.sprites.remove(sprite)
            self.dirty_sprites.discard(sprite)
    
    def update(self, *args, **kwargs):
        """Update all sprites."""
        for sprite in self.sprites[:]:  # Copy list to allow modification during iteration
            sprite.update(*args, **kwargs)
    
    def draw(self, surface: pygame.Surface):
        """Draw all sprites with batching optimization."""
        # Sort sprites by texture/surface for better batching
        sprites_by_texture = {}
        
        for sprite in self.sprites:
            if hasattr(sprite, 'image') and sprite.image:
                texture_id = id(sprite.image)
                if texture_id not in sprites_by_texture:
                    sprites_by_texture[texture_id] = []
                sprites_by_texture[texture_id].append(sprite)
        
        # Draw sprites batched by texture
        for sprites in sprites_by_texture.values():
            for sprite in sprites:
                if hasattr(sprite, 'rect'):
                    surface.blit(sprite.image, sprite.rect)
    
    def clear(self):
        """Clear all sprites."""
        self.sprites.clear()
        self.dirty_sprites.clear()
    
    def __len__(self):
        return len(self.sprites)
    
    def __iter__(self):
        return iter(self.sprites)

# Global pool manager instance
pool_manager = PoolManager()

def get_pool_manager() -> PoolManager:
    """Get the global pool manager instance."""
    return pool_manager