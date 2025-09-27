"""
Unified Physics System for SS6 Game
Consolidates collision detection and physics calculations to eliminate duplication.
"""

import math
import random
from typing import List, Dict, Any, Optional, Tuple
from base_level import BaseGameObject


class UnifiedPhysicsSystem:
    """
    Centralized physics system for collision detection and object interactions.
    Eliminates duplicate collision code across level classes.
    """

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.collision_frequency = 2  # Check collisions every N frames for performance

    def update_object_physics(self, obj: BaseGameObject, frame_count: int):
        """Update physics for a single game object."""
        obj.update_physics(self.width, self.height)

    def handle_object_collisions(self, objects: List[BaseGameObject], frame_count: int):
        """Handle collisions between all objects using optimized algorithm."""
        if len(objects) < 2 or frame_count % self.collision_frequency != 0:
            return

        # Use spatial partitioning for better performance
        grid = self._create_collision_grid(objects)
        checked_pairs = set()

        for y in range(len(grid)):
            for x in range(len(grid[0])):
                cell_objects = grid[y][x]
                if len(cell_objects) < 2:
                    continue

                # Check collisions within cell and with adjacent cells
                for i, obj1_idx in enumerate(cell_objects):
                    for j in range(i + 1, len(cell_objects)):
                        obj2_idx = cell_objects[j]
                        pair = (min(obj1_idx, obj2_idx), max(obj1_idx, obj2_idx))
                        if pair in checked_pairs:
                            continue
                        checked_pairs.add(pair)

                        obj1 = objects[obj1_idx]
                        obj2 = objects[obj2_idx]

                        if self._check_collision(obj1, obj2):
                            self._resolve_collision(obj1, obj2)

    def _create_collision_grid(self, objects: List[BaseGameObject]) -> List[List[List[int]]]:
        """Create spatial grid for optimized collision detection."""
        grid_size = 120
        grid_cols = (self.width // grid_size) + 1
        grid_rows = (self.height // grid_size) + 1

        grid = [[[] for _ in range(grid_cols)] for _ in range(grid_rows)]

        for i, obj in enumerate(objects):
            if obj.alive:
                grid_x = min(int(obj.x // grid_size), grid_cols - 1)
                grid_y = min(int(obj.y // grid_size), grid_rows - 1)
                grid[grid_y][grid_x].append(i)

        return grid

    def _check_collision(self, obj1: BaseGameObject, obj2: BaseGameObject) -> bool:
        """Check if two objects are colliding."""
        if not (obj1.alive and obj2.alive):
            return False

        dx = obj2.x - obj1.x
        dy = obj2.y - obj1.y
        distance_sq = dx * dx + dy * dy

        # Calculate collision radius based on object size
        radius1 = obj1.size / 1.8
        radius2 = obj2.size / 1.8
        min_distance_sq = (radius1 + radius2) ** 2

        return distance_sq < min_distance_sq and distance_sq > 0

    def _resolve_collision(self, obj1: BaseGameObject, obj2: BaseGameObject):
        """Resolve collision between two objects."""
        dx = obj2.x - obj1.x
        dy = obj2.y - obj1.y
        distance = math.sqrt(dx * dx + dy * dy)

        if distance == 0:
            return

        # Normalize collision vector
        nx = dx / distance
        ny = dy / distance

        # Resolve interpenetration
        overlap = (obj1.size + obj2.size) / 1.8 - distance
        total_mass = obj1.mass + obj2.mass
        push_factor = overlap / total_mass

        obj1.x -= nx * push_factor * obj2.mass
        obj1.y -= ny * push_factor * obj2.mass
        obj2.x += nx * push_factor * obj1.mass
        obj2.y += ny * push_factor * obj1.mass

        # Calculate collision response
        dvx = obj1.dx - obj2.dx
        dvy = obj1.dy - obj2.dy
        dot_product = dvx * nx + dvy * ny

        if dot_product < 0:  # Objects moving toward each other
            impulse = (2 * dot_product) / total_mass
            bounce_factor = 0.85

            obj1.dx -= impulse * obj2.mass * nx * bounce_factor
            obj1.dy -= impulse * obj2.mass * ny * bounce_factor
            obj2.dx += impulse * obj1.mass * nx * bounce_factor
            obj2.dy += impulse * obj1.mass * ny * bounce_factor

    def apply_explosion_force(self, x: float, y: float, force_radius: float,
                            objects: List[BaseGameObject], force_strength: float = 15):
        """Apply explosion force to nearby objects."""
        for obj in objects:
            if not obj.alive:
                continue

            dx = obj.x - x
            dy = obj.y - y
            distance_sq = dx * dx + dy * dy

            if distance_sq < force_radius * force_radius and distance_sq > 0:
                distance = math.sqrt(distance_sq)
                # Force is stronger closer to center
                force = (1 - (distance / force_radius)) * force_strength

                # Apply force to velocity
                if distance > 0:
                    obj.dx += (dx / distance) * force
                    obj.dy += (dy / distance) * force

                # Enable bouncing after explosion
                obj.can_bounce = True


class UnifiedObjectFactory:
    """
    Factory class for creating game objects with consistent behavior.
    Eliminates duplicate object creation code.
    """

    def __init__(self, resource_manager=None):
        self.resource_manager = resource_manager

    def create_letter_object(self, value: str, x: float, y: float) -> BaseGameObject:
        """Create a letter game object."""
        obj = BaseGameObject(x, y, value, "letter")
        obj.size = 240
        obj.mass = random.uniform(140, 160)
        obj.dx = random.choice([-1, -0.5, 0.5, 1]) * 1.5
        obj.dy = random.choice([10, 5.5]) * 1.5 * 1.2
        return obj

    def create_number_object(self, value: str, x: float, y: float) -> BaseGameObject:
        """Create a number game object."""
        obj = BaseGameObject(x, y, value, "number")
        obj.size = 240
        obj.mass = random.uniform(40, 60)
        obj.dx = random.choice([-1, -0.5, 0.5, 1]) * 1.5
        obj.dy = random.choice([6, 11.5]) * 1.5 * 3.2
        return obj

    def create_emoji_object(self, value: str, letter: str, emoji_index: int,
                          x: float, y: float, surface) -> BaseGameObject:
        """Create an emoji game object."""
        obj = BaseGameObject(x, y, f"{letter}_emoji_{emoji_index}", "emoji")
        obj.size = 96
        obj.mass = random.uniform(100, 120)
        obj.dx = random.choice([-1, -0.5, 0.5, 1]) * 1.2
        obj.dy = random.choice([8, 6]) * 1.2
        obj.surface = surface
        obj.letter = letter
        obj.emoji_index = emoji_index
        return obj

    def create_color_dot(self, x: float, y: float, color: Tuple[int, int, int],
                        is_target: bool = False) -> BaseGameObject:
        """Create a color dot game object."""
        obj = BaseGameObject(x, y, f"dot_{color}", "color_dot")
        obj.size = 48
        obj.mass = random.uniform(30, 50)
        obj.dx = random.uniform(-6, 6)
        obj.dy = random.uniform(-6, 6)
        obj.color = color
        obj.target = is_target
        return obj


class UnifiedTargetSystem:
    """
    Manages target tracking and validation across all level types.
    Eliminates duplicate target tracking logic.
    """

    def __init__(self):
        self.current_target_hits = set()
        self.targets_needed = set()

    def reset_target_tracking(self, target_object):
        """Reset tracking for a new target."""
        self.current_target_hits.clear()
        self.targets_needed.clear()

        if target_object:
            # Add target components based on object type
            if hasattr(target_object, 'type'):
                if target_object.type == "letter":
                    self._setup_letter_targets(target_object.value)
                elif target_object.type == "number":
                    self._setup_number_targets(target_object.value)
                elif target_object.type == "color_dot":
                    self._setup_color_targets(target_object.color)
                else:
                    # Generic single target
                    self.targets_needed.add(target_object.value)
            else:
                # Fallback for simple values
                self.targets_needed.add(str(target_object))

    def _setup_letter_targets(self, letter: str):
        """Setup targets for letter (letter + 2 emojis)."""
        self.targets_needed = {
            letter,  # The letter itself
            f"{letter}_emoji_1",  # First emoji
            f"{letter}_emoji_2",  # Second emoji
        }

    def _setup_number_targets(self, number: str):
        """Setup targets for number (just the number)."""
        self.targets_needed = {number}

    def _setup_color_targets(self, color: Tuple[int, int, int]):
        """Setup targets for color dots."""
        self.targets_needed = {f"dot_{color}"}

    def register_hit(self, obj: BaseGameObject) -> bool:
        """Register a hit on a target object. Returns True if target complete."""
        obj_id = obj.value if hasattr(obj, 'value') else str(obj)

        if obj_id in self.targets_needed and obj_id not in self.current_target_hits:
            self.current_target_hits.add(obj_id)
            return self.current_target_hits == self.targets_needed

        return False

    def is_target_complete(self) -> bool:
        """Check if current target is complete."""
        return self.current_target_hits == self.targets_needed

    def get_progress(self) -> Tuple[int, int]:
        """Get target progress (hits, total)."""
        return len(self.current_target_hits), len(self.targets_needed)
