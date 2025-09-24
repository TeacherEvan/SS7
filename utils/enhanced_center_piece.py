"""
Enhanced Center Piece Manager with Smooth Animations
Provides animated center targets with bounce, rotate, and scale effects.
"""

import pygame
import random
import math
from typing import Optional, Tuple, Dict, Any
from settings import FLAME_COLORS, BLACK
from utils.animation_system import AnimatedTarget, get_animation_manager, EaseType, create_breathing_animation

class EnhancedCenterPieceManager:
    """
    Enhanced center piece manager with smooth animations for targets.
    """
    
    def __init__(self, width: int, height: int, display_mode: str, particle_manager, 
                 max_swirl_particles: int = 50, resource_manager=None):
        """
        Initialize the enhanced center piece manager.
        
        Args:
            width: Screen width
            height: Screen height
            display_mode: Current display mode ("DEFAULT" or "QBOARD")
            particle_manager: Reference to particle manager for effects
            max_swirl_particles: Maximum number of swirl particles
            resource_manager: Reference to ResourceManager for cached fonts
        """
        self.width = width
        self.height = height
        self.display_mode = display_mode
        self.particle_manager = particle_manager
        self.max_swirl_particles = max_swirl_particles
        self.resource_manager = resource_manager
        
        # Animation manager
        self.animation_manager = get_animation_manager()
        
        # Player font for center piece - cached for performance
        self.player_font = pygame.font.Font(None, 900)
        self.glow_cache = {}
        
        # Center position
        self.player_x = width // 2
        self.player_y = height // 2
        
        # Current animated target
        self.current_target: Optional[AnimatedTarget] = None
        self.target_text = ""
        self.target_mode = ""
        
        # Color transition state
        self.player_color_transition = 0
        self.player_current_color = FLAME_COLORS[0]
        self.player_next_color = FLAME_COLORS[1]
        
        # Swirl particles - reduce count for QBoard performance
        self.swirl_particles = []
        
        # Convergence state
        self.particles_converging = False
        self.convergence_target = None
        self.convergence_timer = 0
        
        # Animation settings
        self.animation_enabled = True
        self.entrance_animation_type = "scale"  # "scale", "fade", "slide_down", "spiral"
        self.continuous_animation = True
        
        # Initialize swirl particles
        self._create_swirl_particles()
        
    def reset(self):
        """Reset all center piece state for a new level/game."""
        self.player_color_transition = 0
        self.player_current_color = FLAME_COLORS[0]
        self.player_next_color = FLAME_COLORS[1]
        self.swirl_particles = []
        self.particles_converging = False
        self.convergence_target = None
        self.convergence_timer = 0
        
        # Clear current target
        if self.current_target:
            self.animation_manager.remove_target(self.current_target)
            self.current_target = None
        
        self._create_swirl_particles()
        
    def set_animation_settings(self, enabled: bool = True, entrance_type: str = "scale", 
                             continuous: bool = True):
        """
        Configure animation settings.
        
        Args:
            enabled: Whether animations are enabled
            entrance_type: Type of entrance animation
            continuous: Whether to use continuous animations (breathing, floating)
        """
        self.animation_enabled = enabled
        self.entrance_animation_type = entrance_type
        self.continuous_animation = continuous
        
    def update_target(self, target_letter: str, mode: str):
        """
        Update the center target with smooth transitions.
        
        Args:
            target_letter: New target letter/shape
            mode: Game mode ("alphabet", "numbers", "shapes", "clcase")
        """
        # If target changed, create new animated target
        if target_letter != self.target_text or mode != self.target_mode:
            # Remove old target with exit animation
            if self.current_target and self.animation_enabled:
                self.animation_manager.animate_target_exit(
                    self.current_target, "fade"
                )
            
            # Create new target
            self.target_text = target_letter
            self.target_mode = mode
            
            if target_letter and self.animation_enabled:
                # Get current color for the new target
                current_color = self._get_interpolated_color()
                
                # Create animated target
                self.current_target = AnimatedTarget(
                    self.player_x, self.player_y, 
                    self._get_display_text(target_letter, mode),
                    current_color
                )
                
                # Add to animation manager
                self.animation_manager.add_target(self.current_target)
                
                # Animate entrance
                self.animation_manager.animate_target_entrance(
                    self.current_target, self.entrance_animation_type
                )
                
                # Add continuous animations
                if self.continuous_animation:
                    # Breathing animation
                    create_breathing_animation(self.current_target, 0.05, 3.0)
                    
                    # Subtle floating animation for some entrance types
                    if self.entrance_animation_type in ["scale", "fade"]:
                        from utils.animation_system import create_floating_animation
                        create_floating_animation(self.current_target, 8, 4.0)
    
    def trigger_hit_animation(self):
        """Trigger hit animation on current target."""
        if self.current_target and self.animation_enabled:
            self.animation_manager.animate_target_hit(self.current_target)
    
    def trigger_success_animation(self):
        """Trigger success animation with enhanced effects."""
        if self.current_target and self.animation_enabled:
            # Scale pulse
            self.animation_manager.create_target_animation(
                self.current_target, "scale", 1.5, 0.2, EaseType.BOUNCE
            )
            self.animation_manager.create_target_animation(
                self.current_target, "scale", 1.0, 0.3, EaseType.EASE_OUT, delay=0.2
            )
            
            # Glow burst
            self.animation_manager.create_target_animation(
                self.current_target, "glow_intensity", 2.0, 0.1, EaseType.EASE_OUT
            )
            self.animation_manager.create_target_animation(
                self.current_target, "glow_intensity", 0.0, 0.5, EaseType.EASE_IN, delay=0.1
            )
            
            # Color flash effect (change color briefly)
            original_color = self.current_target.color
            self.current_target.color = (255, 255, 255)  # Flash white
            
            def restore_color(anim):
                if self.current_target:
                    self.current_target.color = original_color
            
            self.animation_manager.create_target_animation(
                self.current_target, "alpha", 255, 0.1, EaseType.LINEAR, 
                delay=0.05, callback=restore_color
            )
    
    def update_and_draw(self, screen: pygame.Surface, target_letter: str, mode: str, 
                       offset_x: int = 0, offset_y: int = 0):
        """
        Update and draw the complete center piece with animations.
        
        Args:
            screen: Pygame surface to draw on
            target_letter: Current target letter/shape
            mode: Game mode ("alphabet", "numbers", "shapes", "clcase")
            offset_x: X offset for screen shake
            offset_y: Y offset for screen shake
        """
        # Update target if changed
        self.update_target(target_letter, mode)
        
        # Update swirl particles
        self._update_swirl_particles()
        
        # Draw swirl particles
        self._draw_swirl_particles(screen, offset_x, offset_y)
        
        # Update color transition
        self._update_color_transition()
        
        # Update target color
        if self.current_target:
            self.current_target.color = self._get_interpolated_color()
            
            # Apply screen shake to target position
            self.current_target.x = self.player_x + offset_x
            self.current_target.y = self.player_y + offset_y
        
        # Draw center target (either animated or fallback)
        if self.animation_enabled and self.current_target:
            self.current_target.draw(screen, self.player_font)
        else:
            # Fallback to original drawing method
            self._draw_center_target_fallback(screen, target_letter, mode, offset_x, offset_y)
        
        # Draw shape targets (they don't use text animation)
        if mode == "shapes":
            self._draw_shape_target(screen, target_letter, 
                                  self.player_x + offset_x, self.player_y + offset_y)
    
    def trigger_convergence(self, target_x: int, target_y: int):
        """
        Trigger swirl particles to converge toward a target point.
        
        Args:
            target_x: X coordinate of convergence target
            target_y: Y coordinate of convergence target
        """
        if not self.particles_converging:  # Prevent re-triggering while already converging
            self.particles_converging = True
            self.convergence_target = (target_x, target_y)
            self.convergence_timer = 30  # Duration for convergence (frames)
    
    def _get_display_text(self, target_letter: str, mode: str) -> str:
        """Get the display text for a target."""
        if mode == "clcase":
            return target_letter.upper()
        elif mode == "alphabet" and target_letter == "a":
            return "α"
        else:
            return target_letter
    
    def _create_swirl_particles(self, radius: Optional[int] = None, count: Optional[int] = None):
        """Create particles that swirl around the center point."""
        # Set default values based on display mode - REDUCED FOR QBOARD PERFORMANCE
        if radius is None:
            radius = 120 if self.display_mode == "QBOARD" else 80  # Reduced from 150
        
        if count is None:
            # PERFORMANCE: Significantly reduce particle count for QBoard
            count = 15 if self.display_mode == "QBOARD" else 30  # Reduced from 50/30
        
        # Limit count to max_swirl_particles
        count = min(count, self.max_swirl_particles)
        
        self.swirl_particles = []
        
        for _ in range(count):
            # Create a particle with randomized properties and initial angle
            self.swirl_particles.append({
                "angle": random.uniform(0, math.pi * 2),
                "rotation_speed": random.uniform(0.02, 0.04) * (1 if random.random() > 0.5 else -1),
                "base_distance": random.uniform(0.7, 1.0) * radius,  # Vary distance from center
                "distance": 0,  # Will be calculated each frame
                "color": random.choice(FLAME_COLORS),
                "radius": random.randint(4, 8) if self.display_mode == "DEFAULT" else random.randint(6, 12),
                "pulse_speed": random.uniform(0.5, 1.5),
                "pulse_offset": random.uniform(0, math.pi * 2),
                "convergence": False
            })
            
    def _update_swirl_particles(self):
        """Update swirling particles, handle convergence."""
        # PERFORMANCE: Reduce particle regeneration frequency for QBoard
        regeneration_chance = 0.05 if self.display_mode == "QBOARD" else 0.1
        min_particles = 10 if self.display_mode == "QBOARD" else 20
        
        # Add occasional new particles if count is low
        if len(self.swirl_particles) < min_particles and random.random() < regeneration_chance:
            self._create_swirl_particles(count=5)  # Add fewer particles

        current_time_ms = pygame.time.get_ticks()  # Use milliseconds for smoother pulsing
        particles_to_remove = []

        for particle in self.swirl_particles:
            if self.particles_converging and self.convergence_target:
                # --- Convergence Logic ---
                target_x, target_y = self.convergence_target
                # Calculate vector towards target
                dx = target_x - (self.player_x + particle["distance"] * math.cos(particle["angle"]))
                dy = target_y - (self.player_y + particle["distance"] * math.sin(particle["angle"]))
                dist_to_target = math.hypot(dx, dy)

                if dist_to_target > 15:  # Move until close
                    # Move particle directly towards target
                    move_speed = 8  # Adjust convergence speed
                    particle["angle"] = math.atan2(dy, dx)  # Point towards target
                    # Update distance directly based on speed towards target
                    particle["distance"] = max(0, particle["distance"] - move_speed)  # Move inward
                else:
                    # Particle reached target, mark for removal and explosion
                    particles_to_remove.append(particle)
                    continue
            else:
                # --- Normal Swirling Motion ---
                particle["angle"] += particle["rotation_speed"]
                # Pulsing distance effect
                pulse = math.sin(current_time_ms * 0.001 * particle["pulse_speed"] + particle["pulse_offset"]) * 20  # Pulse magnitude
                particle["distance"] = particle["base_distance"] + pulse

        # --- Handle Removed Particles (Reached Convergence Target) ---
        if particles_to_remove and self.convergence_target:
            target_x, target_y = self.convergence_target
            for particle in particles_to_remove:
                if particle in self.swirl_particles:  # Ensure it wasn't already removed
                    self.swirl_particles.remove(particle)

                # PERFORMANCE: Reduce explosion particles for QBoard
                explosion_particles = 2 if self.display_mode == "QBOARD" else 3
                for _ in range(explosion_particles):
                    explosion_color = particle["color"]
                    self.particle_manager.create_particle(
                        target_x + random.uniform(-5, 5),  # Slight spread
                        target_y + random.uniform(-5, 5),
                        explosion_color,
                        random.uniform(8, 16),  # Smaller explosion particles
                        random.uniform(-1.5, 1.5),
                        random.uniform(-1.5, 1.5),
                        random.randint(20, 40)
                    )

        # --- Reset Convergence State ---
        if self.particles_converging:
            self.convergence_timer -= 1
            if self.convergence_timer <= 0 or not self.swirl_particles:  # Stop if timer runs out or no particles left
                self.particles_converging = False
                self.convergence_target = None
                # Optionally regenerate particles if too few remain
                if len(self.swirl_particles) < min_particles:
                    regenerate_count = 15 if self.display_mode == "QBOARD" else 30
                    self._create_swirl_particles(count=regenerate_count)
                    
    def _draw_swirl_particles(self, screen: pygame.Surface, offset_x: int = 0, offset_y: int = 0):
        """Draw swirling particles around the center."""
        # PERFORMANCE: Simplify glow effects for QBoard
        use_glow = self.display_mode == "DEFAULT"
        
        for particle in self.swirl_particles:
            # Calculate particle position
            x = self.player_x + particle["distance"] * math.cos(particle["angle"])
            y = self.player_y + particle["distance"] * math.sin(particle["angle"])

            # Apply screen shake offset
            draw_x = int(x + offset_x)
            draw_y = int(y + offset_y)

            # Draw particle with optional glow effect
            if use_glow:
                glow_radius = int(particle["radius"] * 1.5)
                if glow_radius <= 0:
                    continue

                # Optimized: Cache and reuse glow surfaces
                cache_key = (particle["color"], glow_radius)
                glow_surface = self.glow_cache.get(cache_key)

                if glow_surface is None:
                    size = glow_radius * 2
                    glow_surface = pygame.Surface((size, size), pygame.SRCALPHA)
                    pygame.draw.circle(glow_surface, (*particle["color"], 60), (glow_radius, glow_radius), glow_radius)
                    self.glow_cache[cache_key] = glow_surface
                
                screen.blit(glow_surface, (draw_x - glow_radius, draw_y - glow_radius))

            # Draw main particle
            pygame.draw.circle(screen, particle["color"], (draw_x, draw_y), particle["radius"])
    
    def _update_color_transition(self):
        """Update smooth color transition for the center target."""
        transition_speed = 0.02
        self.player_color_transition += transition_speed
        if self.player_color_transition >= 1:
            self.player_color_transition = 0
            current_index = FLAME_COLORS.index(self.player_current_color)
            next_index = (current_index + 1) % len(FLAME_COLORS)
            self.player_current_color = FLAME_COLORS[current_index]
            self.player_next_color = FLAME_COLORS[next_index]
            
    def _get_interpolated_color(self) -> Tuple[int, int, int]:
        """Get the current interpolated color for the center target."""
        # Interpolate between current and next color
        r = int(self.player_current_color[0] * (1 - self.player_color_transition) + 
                self.player_next_color[0] * self.player_color_transition)
        g = int(self.player_current_color[1] * (1 - self.player_color_transition) + 
                self.player_next_color[1] * self.player_color_transition)
        b = int(self.player_current_color[2] * (1 - self.player_color_transition) + 
                self.player_next_color[2] * self.player_color_transition)
        return (r, g, b)
    
    def _draw_center_target_fallback(self, screen: pygame.Surface, target_letter: str, 
                                   mode: str, offset_x: int, offset_y: int):
        """Fallback drawing method when animations are disabled."""
        if not target_letter:
            return
            
        center_target_color = self._get_interpolated_color()
        center_x = self.player_x + offset_x
        center_y = self.player_y + offset_y
        
        display_char = self._get_display_text(target_letter, mode)
        player_text = self.player_font.render(display_char, True, center_target_color)
        player_rect = player_text.get_rect(center=(center_x, center_y))
        screen.blit(player_text, player_rect)
        
    def _draw_shape_target(self, screen: pygame.Surface, target_letter: str, 
                          center_x: int, center_y: int):
        """Draw shape-based center target."""
        # Use BLACK color for center target (as in original shapes implementation)
        center_target_color = BLACK
        value = target_letter
        size = 500
        pos = (center_x, center_y)
        
        if value == "Rectangle":
            rect = pygame.Rect(pos[0] - int(size*1.5)//2, pos[1] - size//2, int(size*1.5), size)
            pygame.draw.rect(screen, center_target_color, rect, 8)
        elif value == "Square":
            square_rect = pygame.Rect(pos[0] - size//2, pos[1] - size//2, size, size)
            pygame.draw.rect(screen, center_target_color, square_rect, 8)
        elif value == "Circle":
            pygame.draw.circle(screen, center_target_color, pos, size//2, 8)
        elif value == "Triangle":
            points = [
                (pos[0], pos[1] - size//2),
                (pos[0] - size//2, pos[1] + size//2),
                (pos[0] + size//2, pos[1] + size//2)
            ]
            pygame.draw.polygon(screen, center_target_color, points, 8)
        elif value == "Pentagon":
            points = []
            r_size = size // 2
            for i in range(5):
                angle = math.radians(72 * i - 90)
                points.append((pos[0] + r_size * math.cos(angle), pos[1] + r_size * math.sin(angle)))
            pygame.draw.polygon(screen, center_target_color, points, 8)