"""
Enhanced Animation System for SS6 Super Student Game
Provides smooth animations for targets and game elements.
"""

import math
import time
from enum import Enum
from typing import Any, Callable, Dict, Optional, Tuple

import pygame


class EaseType(Enum):
    """Animation easing types."""

    LINEAR = "linear"
    EASE_IN = "ease_in"
    EASE_OUT = "ease_out"
    EASE_IN_OUT = "ease_in_out"
    BOUNCE = "bounce"
    ELASTIC = "elastic"
    BACK = "back"


class AnimationState(Enum):
    """Animation states."""

    STOPPED = "stopped"
    PLAYING = "playing"
    PAUSED = "paused"
    COMPLETED = "completed"


class Animation:
    """Individual animation instance."""

    def __init__(
        self,
        target_object: Any,
        property_name: str,
        start_value: float,
        end_value: float,
        duration: float,
        ease_type: EaseType = EaseType.LINEAR,
        delay: float = 0.0,
        callback: Optional[Callable] = None,
    ):
        """
        Initialize animation.

        Args:
            target_object: Object to animate
            property_name: Property name to animate
            start_value: Starting value
            end_value: Ending value
            duration: Duration in seconds
            ease_type: Type of easing
            delay: Delay before starting animation
            callback: Function to call when animation completes
        """
        self.target_object = target_object
        self.property_name = property_name
        self.start_value = start_value
        self.end_value = end_value
        self.duration = duration
        self.ease_type = ease_type
        self.delay = delay
        self.callback = callback

        self.current_time = 0.0
        self.state = AnimationState.STOPPED
        self.loop = False
        self.reverse_on_complete = False
        self.original_start = start_value
        self.original_end = end_value

    def start(self):
        """Start the animation."""
        self.state = AnimationState.PLAYING
        self.current_time = 0.0

    def pause(self):
        """Pause the animation."""
        if self.state == AnimationState.PLAYING:
            self.state = AnimationState.PAUSED

    def resume(self):
        """Resume the animation."""
        if self.state == AnimationState.PAUSED:
            self.state = AnimationState.PLAYING

    def stop(self):
        """Stop the animation."""
        self.state = AnimationState.STOPPED
        self.current_time = 0.0

    def set_loop(self, loop: bool, reverse: bool = False):
        """Set animation to loop."""
        self.loop = loop
        self.reverse_on_complete = reverse

    def update(self, dt: float) -> bool:
        """
        Update the animation.

        Args:
            dt: Delta time in seconds

        Returns:
            True if animation is still active
        """
        if self.state != AnimationState.PLAYING:
            return self.state != AnimationState.COMPLETED

        # Handle delay
        if self.delay > 0:
            self.delay -= dt
            return True

        self.current_time += dt

        # Calculate progress (0.0 to 1.0)
        if self.duration <= 0:
            progress = 1.0
        else:
            progress = min(1.0, self.current_time / self.duration)

        # Apply easing
        eased_progress = self._apply_easing(progress)

        # Calculate current value
        current_value = self.start_value + (self.end_value - self.start_value) * eased_progress

        # Set the property value
        if hasattr(self.target_object, self.property_name):
            setattr(self.target_object, self.property_name, current_value)
        elif isinstance(self.target_object, dict):
            self.target_object[self.property_name] = current_value

        # Check if animation is complete
        if progress >= 1.0:
            if self.loop:
                if self.reverse_on_complete:
                    # Swap start and end values
                    self.start_value, self.end_value = self.end_value, self.start_value
                self.current_time = 0.0
            else:
                self.state = AnimationState.COMPLETED
                if self.callback:
                    self.callback(self)
                return False

        return True

    def _apply_easing(self, t: float) -> float:
        """Apply easing function to progress value."""
        if self.ease_type == EaseType.LINEAR:
            return t
        elif self.ease_type == EaseType.EASE_IN:
            return t * t
        elif self.ease_type == EaseType.EASE_OUT:
            return 1 - (1 - t) * (1 - t)
        elif self.ease_type == EaseType.EASE_IN_OUT:
            if t < 0.5:
                return 2 * t * t
            else:
                return 1 - 2 * (1 - t) * (1 - t)
        elif self.ease_type == EaseType.BOUNCE:
            return self._bounce(t)
        elif self.ease_type == EaseType.ELASTIC:
            return self._elastic(t)
        elif self.ease_type == EaseType.BACK:
            return self._back(t)
        else:
            return t

    def _bounce(self, t: float) -> float:
        """Bounce easing function."""
        if t < 1 / 2.75:
            return 7.5625 * t * t
        elif t < 2 / 2.75:
            t -= 1.5 / 2.75
            return 7.5625 * t * t + 0.75
        elif t < 2.5 / 2.75:
            t -= 2.25 / 2.75
            return 7.5625 * t * t + 0.9375
        else:
            t -= 2.625 / 2.75
            return 7.5625 * t * t + 0.984375

    def _elastic(self, t: float) -> float:
        """Elastic easing function."""
        if t == 0 or t == 1:
            return t
        p = 0.3
        s = p / 4
        return -(2 ** (10 * (t - 1))) * math.sin((t - 1 - s) * (2 * math.pi) / p)

    def _back(self, t: float) -> float:
        """Back easing function."""
        s = 1.70158
        return t * t * ((s + 1) * t - s)


class AnimatedTarget:
    """Animated target object for smooth visual effects."""

    def __init__(
        self, x: float, y: float, text: str, color: Tuple[int, int, int] = (255, 255, 255)
    ):
        """Initialize animated target."""
        self.x = x
        self.y = y
        self.original_x = x
        self.original_y = y
        self.text = text
        self.color = color

        # Animation properties
        self.scale = 1.0
        self.rotation = 0.0
        self.alpha = 255
        self.glow_intensity = 0.0
        self.pulse_scale = 1.0
        self.shake_x = 0.0
        self.shake_y = 0.0

        # State
        self.visible = True
        self.animations = []

    def add_animation(self, animation: Animation):
        """Add animation to this target."""
        self.animations.append(animation)

    def update(self, dt: float):
        """Update all animations."""
        active_animations = []
        for animation in self.animations:
            if animation.update(dt):
                active_animations.append(animation)
        self.animations = active_animations

    def draw(self, screen: pygame.Surface, font: pygame.font.Font):
        """Draw the animated target."""
        if not self.visible:
            return

        # Calculate final position with shake
        final_x = self.x + self.shake_x
        final_y = self.y + self.shake_y

        # Create text surface
        text_surface = font.render(self.text, True, self.color)

        # Apply scale and rotation
        if self.scale != 1.0 or self.rotation != 0:
            # Scale
            if self.scale != 1.0:
                new_size = (
                    int(text_surface.get_width() * self.scale * self.pulse_scale),
                    int(text_surface.get_height() * self.scale * self.pulse_scale),
                )
                if new_size[0] > 0 and new_size[1] > 0:
                    text_surface = pygame.transform.scale(text_surface, new_size)

            # Rotate
            if self.rotation != 0:
                text_surface = pygame.transform.rotate(text_surface, self.rotation)

        # Apply alpha
        if self.alpha < 255:
            text_surface.set_alpha(int(self.alpha))

        # Draw glow effect
        if self.glow_intensity > 0:
            glow_surface = text_surface.copy()
            glow_alpha = int(self.glow_intensity * 100)
            glow_surface.set_alpha(glow_alpha)

            # Draw glow in multiple positions for blur effect
            glow_offset = int(self.glow_intensity * 5)
            for dx in range(-glow_offset, glow_offset + 1, 2):
                for dy in range(-glow_offset, glow_offset + 1, 2):
                    if dx != 0 or dy != 0:
                        glow_rect = glow_surface.get_rect(center=(final_x + dx, final_y + dy))
                        screen.blit(glow_surface, glow_rect, special_flags=pygame.BLEND_ADD)

        # Draw main text
        text_rect = text_surface.get_rect(center=(final_x, final_y))
        screen.blit(text_surface, text_rect)


class AnimationManager:
    """Manages all animations in the game."""

    def __init__(self):
        self.animations = []
        self.animated_targets = []

    def add_animation(self, animation: Animation):
        """Add an animation to the manager."""
        self.animations.append(animation)
        animation.start()

    def create_target_animation(
        self,
        target: AnimatedTarget,
        property_name: str,
        end_value: float,
        duration: float,
        ease_type: EaseType = EaseType.EASE_OUT,
        delay: float = 0.0,
        callback: Optional[Callable] = None,
    ) -> Animation:
        """Create and add an animation for a target."""
        start_value = getattr(target, property_name)
        animation = Animation(
            target, property_name, start_value, end_value, duration, ease_type, delay, callback
        )
        target.add_animation(animation)
        animation.start()
        return animation

    def animate_target_entrance(self, target: AnimatedTarget, animation_type: str = "scale"):
        """Animate target entrance with various effects."""
        if animation_type == "scale":
            # Scale from 0 to 1
            target.scale = 0.0
            self.create_target_animation(target, "scale", 1.0, 0.5, EaseType.BOUNCE)

        elif animation_type == "fade":
            # Fade from transparent to opaque
            target.alpha = 0
            self.create_target_animation(target, "alpha", 255, 0.3, EaseType.EASE_OUT)

        elif animation_type == "slide_down":
            # Slide down from above
            target.y = target.original_y - 200
            self.create_target_animation(target, "y", target.original_y, 0.4, EaseType.EASE_OUT)

        elif animation_type == "spiral":
            # Spiral in with scale and rotation
            target.scale = 0.0
            target.rotation = 360
            self.create_target_animation(target, "scale", 1.0, 0.6, EaseType.EASE_OUT)
            self.create_target_animation(target, "rotation", 0, 0.6, EaseType.EASE_OUT)

    def animate_target_hit(self, target: AnimatedTarget):
        """Animate target when hit."""
        # Quick scale pulse
        self.create_target_animation(target, "scale", 1.3, 0.1, EaseType.EASE_OUT)
        self.create_target_animation(target, "scale", 1.0, 0.1, EaseType.EASE_IN, delay=0.1)

        # Glow effect
        self.create_target_animation(target, "glow_intensity", 1.0, 0.1, EaseType.EASE_OUT)
        self.create_target_animation(
            target, "glow_intensity", 0.0, 0.2, EaseType.EASE_IN, delay=0.1
        )

        # Shake effect
        def shake_callback(anim):
            target.shake_x = 0
            target.shake_y = 0

        for i in range(5):  # 5 shake iterations
            delay = i * 0.02
            shake_amount = 5 - i  # Decrease shake amount
            self.create_target_animation(
                target, "shake_x", shake_amount, 0.01, EaseType.LINEAR, delay=delay
            )
            self.create_target_animation(
                target, "shake_x", -shake_amount, 0.01, EaseType.LINEAR, delay=delay + 0.01
            )
            if i == 4:  # Last iteration
                self.create_target_animation(
                    target,
                    "shake_x",
                    0,
                    0.01,
                    EaseType.LINEAR,
                    delay=delay + 0.02,
                    callback=shake_callback,
                )

    def animate_target_exit(self, target: AnimatedTarget, animation_type: str = "scale"):
        """Animate target exit."""
        if animation_type == "scale":
            # Scale to 0
            self.create_target_animation(
                target,
                "scale",
                0.0,
                0.3,
                EaseType.EASE_IN,
                callback=lambda anim: setattr(target, "visible", False),
            )

        elif animation_type == "fade":
            # Fade out
            self.create_target_animation(
                target,
                "alpha",
                0,
                0.3,
                EaseType.EASE_IN,
                callback=lambda anim: setattr(target, "visible", False),
            )

        elif animation_type == "spin_out":
            # Spin and scale out
            self.create_target_animation(target, "rotation", 720, 0.5, EaseType.EASE_IN)
            self.create_target_animation(
                target,
                "scale",
                0.0,
                0.5,
                EaseType.EASE_IN,
                callback=lambda anim: setattr(target, "visible", False),
            )

    def create_continuous_pulse(
        self, target: AnimatedTarget, intensity: float = 0.1, speed: float = 2.0
    ):
        """Create a continuous pulsing animation."""
        animation = Animation(
            target, "pulse_scale", 1.0, 1.0 + intensity, speed / 2, EaseType.EASE_IN_OUT
        )
        animation.set_loop(True, reverse=True)
        target.add_animation(animation)
        animation.start()

    def add_target(self, target: AnimatedTarget):
        """Add animated target to manager."""
        self.animated_targets.append(target)

    def remove_target(self, target: AnimatedTarget):
        """Remove animated target from manager."""
        if target in self.animated_targets:
            self.animated_targets.remove(target)

    def update(self, dt: float):
        """Update all animations."""
        # Update standalone animations
        active_animations = []
        for animation in self.animations:
            if animation.update(dt):
                active_animations.append(animation)
        self.animations = active_animations

        # Update animated targets
        for target in self.animated_targets:
            target.update(dt)

    def draw_targets(self, screen: pygame.Surface, font: pygame.font.Font):
        """Draw all animated targets."""
        for target in self.animated_targets:
            target.draw(screen, font)

    def clear_all(self):
        """Clear all animations and targets."""
        self.animations.clear()
        self.animated_targets.clear()

    def pause_all(self):
        """Pause all animations."""
        for animation in self.animations:
            animation.pause()
        for target in self.animated_targets:
            for animation in target.animations:
                animation.pause()

    def resume_all(self):
        """Resume all animations."""
        for animation in self.animations:
            animation.resume()
        for target in self.animated_targets:
            for animation in target.animations:
                animation.resume()


# Utility functions for common animation patterns
def create_floating_animation(target: AnimatedTarget, amplitude: float = 10, speed: float = 3):
    """Create a floating up-down animation."""
    original_y = target.y
    animation = Animation(
        target, "y", original_y, original_y - amplitude, speed / 2, EaseType.EASE_IN_OUT
    )
    animation.set_loop(True, reverse=True)
    target.add_animation(animation)
    animation.start()


def create_breathing_animation(
    target: AnimatedTarget, scale_amount: float = 0.05, speed: float = 2
):
    """Create a breathing scale animation."""
    animation = Animation(target, "scale", 1.0, 1.0 + scale_amount, speed / 2, EaseType.EASE_IN_OUT)
    animation.set_loop(True, reverse=True)
    target.add_animation(animation)
    animation.start()


def create_rotation_animation(target: AnimatedTarget, speed: float = 1):
    """Create a continuous rotation animation."""
    animation = Animation(target, "rotation", 0, 360, speed, EaseType.LINEAR)
    animation.set_loop(True, reverse=False)
    target.add_animation(animation)
    animation.start()


# Global animation manager instance
animation_manager = AnimationManager()


def get_animation_manager() -> AnimationManager:
    """Get the global animation manager instance."""
    return animation_manager
