"""
Enhanced Particle System for SS6 Super Student Game
Uses object pooling and texture atlasing for better performance.
"""

import math
import random
from typing import Any, Dict, List, Optional, Tuple

import pygame

from utils.object_pooling import get_pool_manager
from utils.texture_atlas import get_atlas_manager


class EnhancedParticle:
    """Enhanced particle with more features and better performance."""

    def __init__(self):
        self.reset()

    def reset(self):
        """Reset particle to default state."""
        self.x = 0.0
        self.y = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self.ax = 0.0  # Acceleration
        self.ay = 0.0
        self.life = 1.0
        self.max_life = 1.0
        self.color = (255, 255, 255, 255)
        self.size = 3.0
        self.scale = 1.0
        self.rotation = 0.0
        self.angular_velocity = 0.0
        self.active = False
        self.texture_name = None
        self.blend_mode = pygame.BLEND_ALPHA_SDL2
        self.fade_out = True
        self.physics_enabled = True

    def initialize(
        self,
        x: float,
        y: float,
        vx: float,
        vy: float,
        life: float,
        color: Tuple[int, int, int, int] = (255, 255, 255, 255),
        size: float = 3.0,
        texture_name: str = None,
    ):
        """Initialize particle with given parameters."""
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = life
        self.max_life = life
        self.color = color
        self.size = size
        self.texture_name = texture_name
        self.active = True
        self.scale = 1.0
        self.rotation = 0.0
        self.angular_velocity = random.uniform(-180, 180)  # degrees per second

        # Add some randomness to acceleration for organic movement
        self.ax = random.uniform(-10, 10)
        self.ay = random.uniform(20, 50)  # Slight downward gravity

    def update(self, dt: float) -> bool:
        """
        Update particle state.

        Args:
            dt: Delta time in seconds

        Returns:
            True if particle is still active
        """
        if not self.active:
            return False

        # Update physics
        if self.physics_enabled:
            self.vx += self.ax * dt
            self.vy += self.ay * dt
            self.x += self.vx * dt
            self.y += self.vy * dt

        # Update rotation
        self.rotation += self.angular_velocity * dt
        if self.rotation > 360:
            self.rotation -= 360
        elif self.rotation < 0:
            self.rotation += 360

        # Update life
        self.life -= dt

        # Update scale based on life (for fade effects)
        if self.fade_out:
            self.scale = self.life / self.max_life

        # Check if particle should die
        if self.life <= 0:
            self.active = False
            return False

        return True

    def draw(self, screen: pygame.Surface, atlas_manager=None):
        """Draw the particle."""
        if not self.active:
            return

        # Calculate alpha based on life
        alpha = int(255 * (self.life / self.max_life)) if self.fade_out else self.color[3]
        current_color = (*self.color[:3], alpha)

        # Calculate final size
        final_size = max(1, int(self.size * self.scale))

        if self.texture_name and atlas_manager:
            # Use texture from atlas
            texture = atlas_manager.get_texture("particles", self.texture_name)
            if texture:
                # Scale and rotate texture if needed
                if self.scale != 1.0 or self.rotation != 0:
                    scaled_size = (
                        int(texture.get_width() * self.scale),
                        int(texture.get_height() * self.scale),
                    )
                    if scaled_size[0] > 0 and scaled_size[1] > 0:
                        texture = pygame.transform.scale(texture, scaled_size)

                    if self.rotation != 0:
                        texture = pygame.transform.rotate(texture, self.rotation)

                # Apply color tint
                texture = texture.copy()
                texture.fill(current_color[:3], special_flags=pygame.BLEND_MULT)
                if alpha < 255:
                    texture.set_alpha(alpha)

                # Draw texture
                rect = texture.get_rect(center=(int(self.x), int(self.y)))
                screen.blit(texture, rect, special_flags=self.blend_mode)
                return

        # Fallback to circle drawing
        if final_size > 0:
            # Create surface with alpha
            particle_surf = pygame.Surface((final_size * 2, final_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surf, current_color, (final_size, final_size), final_size)

            # Draw to screen
            screen.blit(
                particle_surf,
                (int(self.x - final_size), int(self.y - final_size)),
                special_flags=self.blend_mode,
            )


class EnhancedParticleSystem:
    """Enhanced particle system with better performance and features."""

    def __init__(self, max_particles: int = 500):
        self.max_particles = max_particles
        self.particles: List[EnhancedParticle] = []
        self.pool_manager = get_pool_manager()
        self.atlas_manager = get_atlas_manager()

        # Performance settings
        self.culling_enabled = True
        self.culling_margin = 100  # Pixels outside screen to keep particles
        self.screen_width = 1920
        self.screen_height = 1080

        # Statistics
        self.stats = {
            "particles_created": 0,
            "particles_culled": 0,
            "particles_expired": 0,
            "draw_calls": 0,
        }

    def set_screen_size(self, width: int, height: int):
        """Set screen size for culling calculations."""
        self.screen_width = width
        self.screen_height = height

    def create_particle_burst(
        self,
        x: float,
        y: float,
        count: int = 20,
        color: Tuple[int, int, int, int] = (255, 255, 255, 255),
        speed_range: Tuple[float, float] = (50, 200),
        life_range: Tuple[float, float] = (0.5, 2.0),
        size_range: Tuple[float, float] = (2, 8),
        texture_name: str = None,
    ) -> List[EnhancedParticle]:
        """
        Create a burst of particles.

        Args:
            x, y: Position to create burst
            count: Number of particles to create
            color: Particle color
            speed_range: Min/max initial speed
            life_range: Min/max particle lifetime
            size_range: Min/max particle size
            texture_name: Optional texture name from atlas

        Returns:
            List of created particles
        """
        created_particles = []

        for _ in range(count):
            if len(self.particles) >= self.max_particles:
                break

            # Get particle from pool
            particle = EnhancedParticle()

            # Random properties
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(*speed_range)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            life = random.uniform(*life_range)
            size = random.uniform(*size_range)

            # Add some color variation
            color_variation = (
                max(0, min(255, color[0] + random.randint(-30, 30))),
                max(0, min(255, color[1] + random.randint(-30, 30))),
                max(0, min(255, color[2] + random.randint(-30, 30))),
                color[3],
            )

            particle.initialize(x, y, vx, vy, life, color_variation, size, texture_name)
            self.particles.append(particle)
            created_particles.append(particle)
            self.stats["particles_created"] += 1

        return created_particles

    def create_explosion(self, x: float, y: float, intensity: float = 1.0):
        """Create an explosion effect."""
        base_count = int(30 * intensity)
        base_speed = 150 * intensity

        # Main explosion particles
        self.create_particle_burst(
            x,
            y,
            base_count,
            color=(255, 150, 50, 255),
            speed_range=(base_speed * 0.5, base_speed * 1.5),
            life_range=(0.8, 1.5),
            size_range=(4, 12),
            texture_name="particle_8_0",  # Red particle
        )

        # Smoke particles
        self.create_particle_burst(
            x,
            y,
            int(base_count * 0.5),
            color=(100, 100, 100, 180),
            speed_range=(base_speed * 0.2, base_speed * 0.8),
            life_range=(1.5, 3.0),
            size_range=(8, 16),
            texture_name="particle_12_6",  # White particle for smoke
        )

        # Sparks
        self.create_particle_burst(
            x,
            y,
            int(base_count * 0.3),
            color=(255, 255, 100, 255),
            speed_range=(base_speed * 0.8, base_speed * 2.0),
            life_range=(0.3, 0.8),
            size_range=(1, 4),
            texture_name="particle_4_3",  # Yellow spark particle
        )

    def create_success_effect(self, x: float, y: float):
        """Create a success/celebration effect."""
        colors = [
            (100, 255, 100, 255),  # Green
            (255, 255, 100, 255),  # Yellow
            (100, 255, 255, 255),  # Cyan
            (255, 100, 255, 255),  # Magenta
        ]

        for color in colors:
            self.create_particle_burst(
                x + random.uniform(-20, 20),
                y + random.uniform(-20, 20),
                count=15,
                color=color,
                speed_range=(80, 150),
                life_range=(1.0, 2.0),
                size_range=(3, 8),
            )

    def update(self, dt: float):
        """Update all particles."""
        particles_to_remove = []

        for particle in self.particles:
            if not particle.update(dt):
                particles_to_remove.append(particle)
                self.stats["particles_expired"] += 1
                continue

            # Culling
            if self.culling_enabled:
                if (
                    particle.x < -self.culling_margin
                    or particle.x > self.screen_width + self.culling_margin
                    or particle.y < -self.culling_margin
                    or particle.y > self.screen_height + self.culling_margin
                ):
                    particles_to_remove.append(particle)
                    self.stats["particles_culled"] += 1

        # Remove inactive particles
        for particle in particles_to_remove:
            if particle in self.particles:
                self.particles.remove(particle)

    def draw(self, screen: pygame.Surface):
        """Draw all particles."""
        self.stats["draw_calls"] = 0

        for particle in self.particles:
            particle.draw(screen, self.atlas_manager)
            self.stats["draw_calls"] += 1

    def clear(self):
        """Clear all particles."""
        self.particles.clear()

    def get_particle_count(self) -> int:
        """Get current number of active particles."""
        return len(self.particles)

    def get_stats(self) -> Dict[str, Any]:
        """Get particle system statistics."""
        return {
            **self.stats,
            "active_particles": len(self.particles),
            "max_particles": self.max_particles,
        }

    def reset_stats(self):
        """Reset statistics counters."""
        self.stats = {
            "particles_created": 0,
            "particles_culled": 0,
            "particles_expired": 0,
            "draw_calls": 0,
        }


# Factory functions for common particle effects
def create_hit_effect(
    particle_system: EnhancedParticleSystem,
    x: float,
    y: float,
    color: Tuple[int, int, int, int] = (255, 100, 100, 255),
):
    """Create a hit/impact effect."""
    particle_system.create_particle_burst(
        x, y, count=15, color=color, speed_range=(30, 100), life_range=(0.3, 0.8), size_range=(2, 6)
    )


def create_trail_effect(
    particle_system: EnhancedParticleSystem,
    x: float,
    y: float,
    color: Tuple[int, int, int, int] = (100, 100, 255, 180),
):
    """Create a trail effect for moving objects."""
    particle_system.create_particle_burst(
        x, y, count=3, color=color, speed_range=(10, 30), life_range=(0.5, 1.0), size_range=(3, 8)
    )
