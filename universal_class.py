"""
Universal Classes for SuperStudent Game

This script contains a collection of universal classes designed to be used across
multiple game levels and modes within the SuperStudent game. Each class
manages a specific aspect of the game's functionality, promoting code reuse
and modularity.

Index of Classes:
- MultiTouchManager: Handles multi-touch input and event processing. (Lines 9-128)
- GlassShatterManager: Manages visual glass shatter effects and screen refresh. (Lines 130-466)
- HUDManager: Displays Heads-Up Display elements (score, ability, etc.). (Lines 468-665)
- CheckpointManager: Manages checkpoint screens and game state restoration. (Lines 667-874)
- FlamethrowerManager: Handles flamethrower visual effects. (Lines 876-998)
- CenterPieceManager: Manages the central target display and associated effects. (Lines 1000-1316)

Dependencies:
- pygame: For graphics, event handling, and game loop.
- random: For generating random numbers used in effects and game logic.
- math: For mathematical calculations (e.g., angles, distances).
- settings: For game-specific constants (colors, durations, etc.).
"""
import pygame
import random
import math
from settings import (
    WHITE, BLACK, FLAME_COLORS
)

class MultiTouchManager:
    """
    Universal class to manage multi-touch events and prevent duplicate handling.
    Handles touch tracking, coordinate conversion, and touch event processing.
    """
    
    def __init__(self, width, height):
        """
        Initialize the multi-touch manager.
        
        Args:
            width (int): Screen width for coordinate conversion
            height (int): Screen height for coordinate conversion
        """
        self.width = width
        self.height = height
        self.active_touches = {}
        self._touch_cooldown = {}  # Prevent rapid touch spam
        self._cooldown_duration = 50  # milliseconds
        
    def reset(self):
        """Reset all touch state for a new level/game."""
        self.active_touches = {}
        self._touch_cooldown = {}
        
    def handle_touch_down(self, event):
        """
        Handle FINGERDOWN event and convert to screen coordinates.
        
        Args:
            event: pygame FINGERDOWN event
            
        Returns:
            tuple: (touch_id, touch_x, touch_y) or None if touch should be ignored
        """
        touch_id = event.finger_id
        touch_x = event.x * self.width
        touch_y = event.y * self.height
        
        # Check cooldown to prevent spam
        current_time = pygame.time.get_ticks()
        if touch_id in self._touch_cooldown:
            if current_time - self._touch_cooldown[touch_id] < self._cooldown_duration:
                return None
                
        self._touch_cooldown[touch_id] = current_time
        self.active_touches[touch_id] = (touch_x, touch_y)
        
        return touch_id, touch_x, touch_y
        
    def handle_touch_up(self, event):
        """
        Handle FINGERUP event.
        
        Args:
            event: pygame FINGERUP event
            
        Returns:
            tuple: (touch_id, last_x, last_y) or None if touch wasn't tracked
        """
        touch_id = event.finger_id
        if touch_id in self.active_touches:
            last_pos = self.active_touches[touch_id]
            del self.active_touches[touch_id]
            return touch_id, last_pos[0], last_pos[1]
        return None
        
    def handle_touch_motion(self, event):
        """
        Handle FINGERMOTION event.
        
        Args:
            event: pygame FINGERMOTION event
            
        Returns:
            tuple: (touch_id, touch_x, touch_y) or None if touch wasn't tracked
        """
        touch_id = event.finger_id
        if touch_id in self.active_touches:
            touch_x = event.x * self.width
            touch_y = event.y * self.height
            self.active_touches[touch_id] = (touch_x, touch_y)
            return touch_id, touch_x, touch_y
        return None
        
    def get_active_touches(self):
        """
        Get all currently active touches.
        
        Returns:
            dict: Dictionary of {touch_id: (x, y)} for all active touches
        """
        return self.active_touches.copy()
        
    def get_touch_count(self):
        """
        Get the number of currently active touches.
        
        Returns:
            int: Number of active touches
        """
        return len(self.active_touches)
        
    def is_touch_active(self, touch_id):
        """
        Check if a specific touch ID is currently active.
        
        Args:
            touch_id: Touch ID to check
            
        Returns:
            bool: True if touch is active, False otherwise
        """
        return touch_id in self.active_touches
        
    def clear_touch(self, touch_id):
        """
        Manually clear a specific touch (useful for cleanup).
        
        Args:
            touch_id: Touch ID to clear
        """
        if touch_id in self.active_touches:
            del self.active_touches[touch_id]
        if touch_id in self._touch_cooldown:
            del self._touch_cooldown[touch_id]

class GlassShatterManager:
    """
    Universal class to manage glass shatter effects and prevent duplicate events.
    Handles crack creation, drawing, background switching, and screen refresh.
    """
    
    def __init__(self, width, height, particle_manager=None):
        """
        Initialize the glass shatter manager.
        
        Args:
            width (int): Screen width
            height (int): Screen height
            particle_manager: Reference to particle manager for shatter effects
        """
        self.width = width
        self.height = height
        self.particle_manager = particle_manager
        
        # Glass crack state
        self.glass_cracks = []
        
        # Background colors
        self.current_background = WHITE
        self.opposite_background = BLACK
        
        # Screen refresh state (30 seconds at 50 fps = 1500 frames)
        self.refresh_timer = 1500
        self.refresh_interval = 1500  # 30 seconds
        
        # Event prevention flags
        self._processing_shatter = False
        self._last_crack_time = 0
        self._crack_cooldown = 5  # Minimum frames between cracks to prevent spam
        
    def reset(self):
        """Reset all glass shatter state for a new level/game."""
        self.glass_cracks = []
        self.refresh_timer = self.refresh_interval
        self._processing_shatter = False
        self._last_crack_time = 0
        self.current_background = WHITE
        self.opposite_background = BLACK
        
    def handle_misclick(self, x, y):
        """
        Handle a misclick event by creating a crack.
        Prevents duplicate events through cooldown system.
        
        Args:
            x (int): X coordinate of the misclick
            y (int): Y coordinate of the misclick
        """
        current_time = pygame.time.get_ticks()
        
        # Prevent spam clicking from creating too many cracks
        if current_time - self._last_crack_time < self._crack_cooldown:
            return
            
        self._last_crack_time = current_time
        
        # Create crack at click position
        self._create_crack(x, y)
        
        # Check if we should trigger shatter effect (visual only, no game over)
        if len(self.glass_cracks) >= 10:  # Hardcoded since MAX_CRACKS will be removed
            self._trigger_shatter()
            
    def _create_crack(self, x, y):
        """
        Create a crack at the specified position with realistic branching.
        
        Args:
            x (int): X coordinate for crack center
            y (int): Y coordinate for crack center
        """
        # Create main crack line with multiple segments for realistic look
        segments = random.randint(3, 6)
        length = random.uniform(80, 150)
        spread_angle = 30  # Maximum angle deviation between segments
        
        # Random starting direction
        current_angle = random.uniform(0, 360)
        
        # Generate main crack segments
        points = [(x, y)]  # Start at click position
        
        for i in range(segments):
            # Add some randomness to direction
            angle_variation = random.uniform(-spread_angle, spread_angle)
            current_angle += angle_variation
            
            # Calculate next point
            rad_angle = math.radians(current_angle)
            segment_length = length / segments * random.uniform(0.7, 1.3)  # Vary segment length
            next_x = points[-1][0] + math.cos(rad_angle) * segment_length
            next_y = points[-1][1] + math.sin(rad_angle) * segment_length
            
            points.append((next_x, next_y))
        
        # Create branches
        branch_points = []
        
        if random.random() < 0.7:  # 70% chance to add branches
            num_branches = random.randint(1, 3)
            
            for _ in range(num_branches):
                # Pick a random segment to branch from
                branch_from = random.randint(0, len(points) - 2)
                branch_angle = current_angle + random.uniform(30, 150)  # Significant deviation
                
                # Create branch segments
                branch_segments = random.randint(2, 4)
                branch_points.append([points[branch_from]])  # Start point
                current_branch_angle = branch_angle
                
                for _ in range(branch_segments):
                    angle_variation = random.uniform(-spread_angle, spread_angle)
                    current_branch_angle += angle_variation
                    
                    rad_angle = math.radians(current_branch_angle)
                    segment_length = random.uniform(0.4, 0.7) * length  # Branches are shorter
                    next_x = branch_points[-1][-1][0] + math.cos(rad_angle) * segment_length
                    next_y = branch_points[-1][-1][1] + math.sin(rad_angle) * segment_length
                    
                    branch_points[-1].append((next_x, next_y))
        
        # Determine crack color based on current background
        draw_crack_color = WHITE if self.current_background == BLACK else BLACK
        
        # Add the crack
        self.glass_cracks.append({
            "points": points,
            "branches": branch_points,
            "width": random.uniform(1, 3),  # Line width
            "alpha": 200,  # Starting opacity
            "color": draw_crack_color
        })
            
    def _trigger_shatter(self):
        """
        Triggers the screen shatter effect (visual only).
        Internal method with duplicate prevention.
        """
        # Prevent multiple simultaneous shatter events
        if self._processing_shatter:
            return
            
        self._processing_shatter = True
        
        # Create shatter particles if particle manager is available
        if self.particle_manager:
            self._create_shatter_particles()
            
        # Reset processing flag after a short delay to prevent immediate re-triggering
        pygame.time.set_timer(pygame.USEREVENT + 1, 100)  # 100ms delay
        
    def _create_shatter_particles(self):
        """Create dramatic shatter particle effects - DISABLED."""
        # Particle effects have been disabled per user request
        # The shatter visual effect now only includes the crack display
        pass
    
    def update(self):
        """
        Update the glass shatter state each frame.
        Call this in the main game loop.
        """
        # Update screen refresh timer
        self.refresh_timer -= 1
        if self.refresh_timer <= 0:
            # Clear all cracks and reset timer
            self.glass_cracks = []
            self.refresh_timer = self.refresh_interval
            
            # Create refresh particle effect if particle manager is available
            if self.particle_manager:
                self._create_refresh_particles()
                
    def _create_refresh_particles(self):
        """Create particle effect when screen refreshes - DISABLED."""
        # Particle effects have been disabled per user request
        # The refresh now only clears cracks without sparkle effects
        pass
            
    def get_screen_shake_offset(self):
        """
        Get the current screen shake offset.
        Screen shake has been disabled - always returns (0, 0).
        
        Returns:
            tuple: (offset_x, offset_y) - always (0, 0) since shake is disabled
        """
        return 0, 0
        
    def get_background_color(self):
        """
        Get the current background color.
        
        Returns:
            tuple: RGB color tuple for background
        """
        return self.current_background
        
    def draw_cracks(self, surface):
        """
        Draw all cracks on the given surface.
        
        Args:
            surface: Pygame surface to draw on
        """
        # Determine crack color based on current background
        draw_crack_color = WHITE if self.current_background == BLACK else BLACK
        
        # Draw all cracks
        for crack in self.glass_cracks:
            # Draw main segments
            for i in range(len(crack["points"]) - 1):
                pygame.draw.line(
                    surface, 
                    draw_crack_color,
                    crack["points"][i], 
                    crack["points"][i+1], 
                    int(crack["width"])
                )
            
            # Draw branches
            for branch in crack["branches"]:
                for i in range(len(branch) - 1):
                    pygame.draw.line(
                        surface, 
                        draw_crack_color,
                        branch[i], 
                        branch[i+1], 
                        int(crack["width"] * 0.7)  # Branches are thinner
                    )
                    
    def handle_event(self, event):
        """
        Handle pygame events related to glass shatter.
        
        Args:
            event: Pygame event object
        """
        if event.type == pygame.USEREVENT + 1:
            # Reset processing flag after shatter delay
            self._processing_shatter = False
            pygame.time.set_timer(pygame.USEREVENT + 1, 0)  # Cancel the timer
            
    def get_crack_count(self):
        """
        Get the current number of cracks.
        
        Returns:
            int: Number of cracks currently on screen
        """
        return len(self.glass_cracks)
        
    def get_refresh_time_remaining(self):
        """
        Get the time remaining until next screen refresh.
        
        Returns:
            int: Frames remaining until refresh
        """
        return self.refresh_timer
        
    def set_background_colors(self, current, opposite):
        """
        Set the background colors for the shatter effect.
        
        Args:
            current: Current background color (RGB tuple)
            opposite: Opposite background color (RGB tuple)
        """
        self.current_background = current
        self.opposite_background = opposite

class HUDManager:
    """
    Universal class to manage HUD (Heads-Up Display) elements.
    Handles score, ability, target, progress display for all game modes.
    """
    
    def __init__(self, width, height, small_font, glass_shatter_manager):
        """
        Initialize the HUD manager.
        
        Args:
            width (int): Screen width
            height (int): Screen height
            small_font: Pygame font object for HUD text
            glass_shatter_manager: Reference to glass shatter manager for background color
        """
        self.width = width
        self.height = height
        self.small_font = small_font
        self.glass_shatter_manager = glass_shatter_manager
        
        # HUD positioning constants
        self.margin = 20
        self.line_height = 40
        
    def display_info(self, screen, score, ability, target_letter, overall_destroyed, total_letters, mode, **kwargs):
        """
        Display the HUD elements (Target, Progress only - Score and Ability removed for performance).
        
        Args:
            screen: Pygame surface to draw on
            score (int): Current score (unused)
            ability (str): Current ability name (unused)
            target_letter (str): Current target letter/shape/color
            overall_destroyed (int): Number of targets destroyed
            total_letters (int): Total targets in level
            mode (str): Game mode ("colors", "alphabet", "numbers", "shapes", "clcase")
            **kwargs: Additional mode-specific parameters
        """
        # Determine text color based on background
        text_color = BLACK if self.glass_shatter_manager.get_background_color() == WHITE else WHITE
        
        # Different layout for colors mode to prevent overlap
        if mode == "colors":
            self._display_colors_hud(screen, target_letter, overall_destroyed, total_letters, text_color, **kwargs)
        else:
            self._display_standard_hud(screen, target_letter, overall_destroyed, total_letters, mode, text_color)
    
    def _display_colors_hud(self, screen, target_letter, overall_destroyed, total_letters, text_color, **kwargs):
        """Display HUD for colors mode with special layout (Score and Ability removed)."""
        # Target color at top left
        target_color_text = self.small_font.render(f"Target Color: {target_letter}", True, text_color)
        screen.blit(target_color_text, (self.margin, self.margin))
        
        # Target dots remaining below target color
        target_dots_left = kwargs.get('target_dots_left', 0)
        if target_dots_left is not None:
            dots_left_text = self.small_font.render(f"Remaining: {target_dots_left}", True, text_color)
            screen.blit(dots_left_text, (self.margin, self.margin + self.line_height))
        
        # Next color progress below remaining dots
        current_color_dots_destroyed = kwargs.get('current_color_dots_destroyed', 0)
        if current_color_dots_destroyed is not None:
            next_color_text = self.small_font.render(f"Next color in: {5 - current_color_dots_destroyed} dots", True, text_color)
            screen.blit(next_color_text, (self.margin, self.margin + self.line_height * 2))
        
        # Progress on top right
        progress_text = self.small_font.render(f"Destroyed: {overall_destroyed}/{total_letters}", True, text_color)
        progress_rect = progress_text.get_rect(topright=(self.width - self.margin, self.margin))
        screen.blit(progress_text, progress_rect)
    
    def _display_standard_hud(self, screen, target_letter, overall_destroyed, total_letters, mode, text_color):
        """Display HUD for standard modes (alphabet, numbers, shapes, clcase) - Score and Ability removed."""
        # Right-aligned elements only
        display_target = self._format_target_display(target_letter, mode)
        
        target_text = self.small_font.render(f"Target: {display_target}", True, text_color)
        target_rect = target_text.get_rect(topright=(self.width - self.margin, self.margin))
        screen.blit(target_text, target_rect)

        progress_text = self.small_font.render(f"Destroyed: {overall_destroyed}/{total_letters}", True, text_color)
        progress_rect = progress_text.get_rect(topright=(self.width - self.margin, self.margin + self.line_height))
        screen.blit(progress_text, progress_rect)
    
    def _format_target_display(self, target_letter, mode):
        """Format the target letter for display based on mode."""
        display_target = target_letter
        
        if (mode == "alphabet" or mode == "clcase") and target_letter == "a":
            display_target = "α"
        elif mode == "clcase":
            display_target = target_letter.upper()
            
        return display_target
    
    def display_collision_status(self, screen, collision_enabled, collision_delay_counter, collision_delay_frames):
        """
        Display collision status for debugging (colors mode).
        
        Args:
            screen: Pygame surface to draw on
            collision_enabled (bool): Whether collisions are enabled
            collision_delay_counter (int): Current delay counter
            collision_delay_frames (int): Total delay frames
        """
        if not collision_enabled:
            text_color = BLACK if self.glass_shatter_manager.get_background_color() == WHITE else WHITE
            countdown_text = f"Collisions in: {(collision_delay_frames - collision_delay_counter) // 50}s"
            countdown_surface = self.small_font.render(countdown_text, True, text_color)
            screen.blit(countdown_surface, (10, self.height - 30))
    
    def display_sample_target(self, screen, target_color, target_radius=24):
        """
        Display a sample target dot for colors mode.
        
        Args:
            screen: Pygame surface to draw on
            target_color: RGB color tuple for the target
            target_radius (int): Radius of the sample dot
        """
        # Show sample target dot reference at top right
        sample_x = self.width - 60
        sample_y = 60
        
        pygame.draw.circle(screen, target_color, (sample_x, sample_y), target_radius)
        pygame.draw.rect(screen, WHITE, (sample_x - 30, sample_y - 30, 60, 60), 2)
        
    def display_screen_refresh_timer(self, screen):
        """
        Display the screen refresh timer showing time until cracks are cleared.
        
        Args:
            screen: Pygame surface to draw on
        """
        text_color = BLACK if self.glass_shatter_manager.get_background_color() == WHITE else WHITE
        refresh_frames = self.glass_shatter_manager.get_refresh_time_remaining()
        refresh_seconds = refresh_frames // 50  # Convert frames to seconds (50 fps)
        
        # Display refresh timer at bottom center
        refresh_text = f"Screen refresh in: {refresh_seconds}s"
        refresh_surface = self.small_font.render(refresh_text, True, text_color)
        refresh_rect = refresh_surface.get_rect(center=(self.width // 2, self.height - 30))
        screen.blit(refresh_surface, refresh_rect)

class CheckpointManager:
    """
    Universal class to manage checkpoint screens across all game modes.
    Handles checkpoint display, user interaction, and state management.
    """
    
    def __init__(self, width, height, fonts, small_font):
        """
        Initialize the checkpoint manager.
        
        Args:
            width (int): Screen width
            height (int): Screen height
            fonts (list): List of pygame font objects
            small_font: Pygame font object for UI text
        """
        self.width = width
        self.height = height
        self.fonts = fonts
        self.small_font = small_font
        
        # Button configuration
        self.button_width = 300
        self.button_height = 80
        self.center_x = width // 2
        self.center_y = height // 2
        
        # Create button rectangles
        self.continue_rect = pygame.Rect(
            (self.center_x - self.button_width - 20, self.center_y + 50), 
            (self.button_width, self.button_height)
        )
        self.menu_rect = pygame.Rect(
            (self.center_x + 20, self.center_y + 50), 
            (self.button_width, self.button_height)
        )
        
    def show_checkpoint_screen(self, screen, mode=None, **kwargs):
        """
        Display the checkpoint screen and handle user interaction.
        
        Args:
            screen: Pygame surface to draw on
            mode (str): Game mode ("colors", "alphabet", "numbers", "shapes", "clcase")
            **kwargs: Additional mode-specific parameters for state restoration
            
        Returns:
            bool: True if Continue was selected, False if Menu was selected
        """
        # Store original state for colors mode
        original_state = self._store_colors_state(mode, **kwargs)
        
        running = True
        clock = pygame.time.Clock()
        color_transition = 0.0
        current_color = FLAME_COLORS[0]
        next_color = FLAME_COLORS[1]
        
        # Create swirling particles for visual effect
        swirling_particles = self._create_swirling_particles()
        
        while running:
            screen.fill(BLACK)
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    if self.continue_rect.collidepoint(mx, my):
                        # Restore colors mode state if needed
                        if mode == "colors" and original_state:
                            self._restore_colors_state(original_state)
                        return True  # Continue game
                    elif self.menu_rect.collidepoint(mx, my):
                        return False  # Return to level menu
            
            # Update and draw swirling particles
            self._update_swirling_particles(swirling_particles, screen)
            
            # Update color transition for heading
            color_transition += 0.02
            if color_transition >= 1:
                color_transition = 0
                current_color = next_color
                next_color = random.choice(FLAME_COLORS)
            
            # Interpolate colors
            r = int(current_color[0] * (1 - color_transition) + next_color[0] * color_transition)
            g = int(current_color[1] * (1 - color_transition) + next_color[1] * color_transition)
            b = int(current_color[2] * (1 - color_transition) + next_color[2] * color_transition)
            heading_color = (r, g, b)
            
            # Draw heading
            checkpoint_font = self.fonts[2]
            checkpoint_text = checkpoint_font.render("Checkpoint!", True, heading_color)
            checkpoint_rect = checkpoint_text.get_rect(center=(self.center_x, self.center_y - 150))
            screen.blit(checkpoint_text, checkpoint_rect)
            
            # Additional message
            subtext = self.small_font.render("Well done! You've completed this task!", True, WHITE)
            subtext_rect = subtext.get_rect(center=(self.center_x, self.center_y - 100))
            screen.blit(subtext, subtext_rect)
            
            # Draw buttons with neon effect
            self._draw_neon_button(screen, self.continue_rect, (0, 255, 0))  # Green for continue
            self._draw_neon_button(screen, self.menu_rect, (255, 165, 0))    # Orange for menu
            
            # Change button text based on mode
            if mode == "shapes":
                cont_text = self.small_font.render("Replay Level", True, WHITE)
            else:
                cont_text = self.small_font.render("Continue", True, WHITE)
            menu_text = self.small_font.render("Level Select", True, WHITE)
            
            screen.blit(cont_text, cont_text.get_rect(center=self.continue_rect.center))
            screen.blit(menu_text, menu_text.get_rect(center=self.menu_rect.center))
            
            pygame.display.flip()
            clock.tick(60)
    
    def _store_colors_state(self, mode, **kwargs):
        """Store colors mode state for restoration after checkpoint."""
        if mode != "colors":
            return None
            
        # Import globals only when needed to avoid circular imports
        import __main__
        
        try:
            return {
                'color_idx': getattr(__main__, 'color_idx', 0),
                'color_sequence': getattr(__main__, 'color_sequence', []).copy() if hasattr(__main__, 'color_sequence') else None,
                'next_color_index': getattr(__main__, 'next_color_index', 0),
                'target_dots_left': getattr(__main__, 'target_dots_left', 10),
                'used_colors': getattr(__main__, 'used_colors', []).copy() if hasattr(__main__, 'used_colors') else []
            }
        except:
            # Fallback if globals aren't available
            return {
                'color_idx': kwargs.get('color_idx', 0),
                'color_sequence': kwargs.get('color_sequence', []).copy() if kwargs.get('color_sequence') else None,
                'next_color_index': kwargs.get('next_color_index', 0),
                'target_dots_left': kwargs.get('target_dots_left', 10),
                'used_colors': kwargs.get('used_colors', []).copy() if kwargs.get('used_colors') else []
            }
    
    def _restore_colors_state(self, original_state):
        """Restore colors mode state after checkpoint."""
        # Import globals only when needed to avoid circular imports
        import __main__
        
        try:
            if 'color_idx' in original_state:
                __main__.color_idx = original_state['color_idx']
            if 'target_dots_left' in original_state:
                __main__.target_dots_left = original_state['target_dots_left']
            if original_state.get('color_sequence') is not None:
                __main__.color_sequence = original_state['color_sequence']
            if 'next_color_index' in original_state:
                __main__.next_color_index = original_state['next_color_index']
            if original_state.get('used_colors'):
                __main__.used_colors = original_state['used_colors']
        except:
            # Silently fail if globals can't be set
            pass
    
    def _create_swirling_particles(self):
        """Create swirling particles for visual effect."""
        swirling_particles = []
        for _ in range(150):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(100, max(self.width, self.height) * 0.6)
            angular_speed = random.uniform(0.01, 0.03) * random.choice([-1, 1])
            radius = random.randint(5, 10)
            color = random.choice(FLAME_COLORS)
            swirling_particles.append({
                "angle": angle, 
                "distance": distance, 
                "angular_speed": angular_speed,
                "radius": radius, 
                "color": color
            })
        return swirling_particles
    
    def _update_swirling_particles(self, swirling_particles, screen):
        """Update and draw swirling particles."""
        for particle in swirling_particles:
            particle["angle"] += particle["angular_speed"]
            x = self.center_x + particle["distance"] * math.cos(particle["angle"])
            y = self.center_y + particle["distance"] * math.sin(particle["angle"])
            pygame.draw.circle(screen, particle["color"], (int(x), int(y)), particle["radius"])
            
            # Keep particles within reasonable boundary
            if particle["distance"] > max(self.width, self.height) * 0.8:
                particle["distance"] = random.uniform(50, 200)
    
    def _draw_neon_button(self, screen, rect, color):
        """Draw a neon-style button with glow effect."""
        # Draw multiple layers for glow effect
        for i in range(5):
            glow_rect = pygame.Rect(
                rect.x - i * 2, rect.y - i * 2, 
                rect.width + i * 4, rect.height + i * 4
            )
            alpha = max(0, 100 - i * 20)
            glow_color = (*color, alpha)
            
            # Create surface with alpha for glow
            glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, glow_color, (0, 0, glow_rect.width, glow_rect.height), 2)
            screen.blit(glow_surface, (glow_rect.x, glow_rect.y))
        
        # Draw main button
        pygame.draw.rect(screen, color, rect, 3)

class FlamethrowerManager:
    """
    Universal class to manage flamethrower effects across all levels except colors.
    Handles flamethrower creation, drawing, and animation.
    """
    
    def __init__(self):
        """Initialize the flamethrower manager."""
        self.flamethrowers = []
        self.glow_cache = {}
        
    def create_flamethrower(self, start_x, start_y, end_x, end_y, colors=None, widths=None, duration=10):
        """
        Create a new flamethrower effect.
        
        Args:
            start_x (int): Starting X coordinate
            start_y (int): Starting Y coordinate
            end_x (int): Ending X coordinate
            end_y (int): Ending Y coordinate
            colors (list): List of colors for the flame effect
            widths (list): List of widths for the flame effect
            duration (int): Duration of the effect in frames
        """
        if colors is None:
            colors = FLAME_COLORS
        if widths is None:
            widths = [20, 30, 40]
            
        self.flamethrowers.append({
            "start_pos": (start_x, start_y),
            "end_pos": (end_x, end_y),
            "colors": colors,
            "widths": widths,
            "duration": duration,
            "type": "flamethrower"
        })
        
    def update(self):
        """Update all active flamethrowers."""
        flamethrowers_to_remove = []
        
        for flamethrower in self.flamethrowers:
            flamethrower["duration"] -= 1
            if flamethrower["duration"] <= 0:
                flamethrowers_to_remove.append(flamethrower)
                
        # Remove expired flamethrowers
        for flamethrower in flamethrowers_to_remove:
            self.flamethrowers.remove(flamethrower)
            
    def draw(self, screen, offset_x=0, offset_y=0):
        """
        Draw all active flamethrowers.
        
        Args:
            screen: Pygame surface to draw on
            offset_x (int): X offset for screen shake
            offset_y (int): Y offset for screen shake
        """
        for flamethrower in self.flamethrowers:
            self._draw_flamethrower(screen, flamethrower, offset_x, offset_y)
            
    def _draw_flamethrower(self, screen, flamethrower, offset_x=0, offset_y=0):
        """
        Draw a single flamethrower effect using circles along a line.
        
        Args:
            screen: Pygame surface to draw on
            flamethrower: Flamethrower data dictionary
            offset_x (int): X offset for screen shake
            offset_y (int): Y offset for screen shake
        """
        start_x = flamethrower["start_pos"][0] + offset_x
        start_y = flamethrower["start_pos"][1] + offset_y
        end_x = flamethrower["end_pos"][0] + offset_x
        end_y = flamethrower["end_pos"][1] + offset_y
        
        # Calculate line properties
        dx = end_x - start_x
        dy = end_y - start_y
        distance = math.hypot(dx, dy)
        
        if distance == 0:
            return
            
        # Draw flame circles along the line
        num_circles = max(1, int(distance // 15))  # Circle every 15 pixels, minimum 1
        for i in range(num_circles):
            if num_circles == 1:
                t = 0.5  # Center the single circle
            else:
                t = i / (num_circles - 1)  # Interpolation factor
            circle_x = int(start_x + t * dx)
            circle_y = int(start_y + t * dy)
            
            # Vary circle size and color
            base_radius = random.choice(flamethrower.get("widths", [20, 30, 40])) // 4
            radius = max(1, base_radius + random.randint(-5, 5))  # Ensure minimum radius of 1
            color = random.choice(flamethrower.get("colors", FLAME_COLORS))
            
            # Add some randomness to position for flame effect
            jitter_x = random.randint(-8, 8)
            jitter_y = random.randint(-8, 8)
            
            # Calculate glow radius and ensure it's valid
            glow_radius = max(1, int(radius * 1.5))
            
            # Draw glow effect
            if glow_radius > 0:
                # Optimized: Cache and reuse glow surfaces
                cache_key = (color, glow_radius)
                glow_surface = self.glow_cache.get(cache_key)

                if glow_surface is None:
                    size = glow_radius * 2
                    glow_surface = pygame.Surface((size, size), pygame.SRCALPHA)
                    pygame.draw.circle(glow_surface, (*color, 100), (glow_radius, glow_radius), glow_radius)
                    self.glow_cache[cache_key] = glow_surface

                screen.blit(glow_surface, (circle_x + jitter_x - glow_radius, circle_y + jitter_y - glow_radius))
            
            # Draw main flame circle
            if radius > 0:
                pygame.draw.circle(screen, color, (circle_x + jitter_x, circle_y + jitter_y), radius)
                
    def clear(self):
        """Clear all flamethrowers."""
        self.flamethrowers.clear()
        
    def get_count(self):
        """Get the number of active flamethrowers."""
        return len(self.flamethrowers)

class CenterPieceManager:
    """
    Universal class to manage center piece functionality for all levels except colors.
    Handles center target display, swirl particles, color transitions, and convergence effects.
    """
    
    def __init__(self, width, height, display_mode, particle_manager, max_swirl_particles=50, resource_manager=None):
        """
        Initialize the center piece manager.
        
        Args:
            width (int): Screen width
            height (int): Screen height
            display_mode (str): Current display mode ("DEFAULT" or "QBOARD")
            particle_manager: Reference to particle manager for effects
            max_swirl_particles (int): Maximum number of swirl particles
            resource_manager: Reference to ResourceManager for cached fonts
        """
        self.width = width
        self.height = height
        self.display_mode = display_mode
        self.particle_manager = particle_manager
        self.max_swirl_particles = max_swirl_particles
        self.resource_manager = resource_manager
        
        # Player font for center piece - cached for performance
        self.player_font = pygame.font.Font(None, 900)
        self.glow_cache = {}
        
        # Center position
        self.player_x = width // 2
        self.player_y = height // 2
        
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
        self._create_swirl_particles()
        
    def update_and_draw(self, screen, target_letter, mode, offset_x=0, offset_y=0):
        """
        Update and draw the complete center piece.
        
        Args:
            screen: Pygame surface to draw on
            target_letter (str): Current target letter/shape
            mode (str): Game mode ("alphabet", "numbers", "shapes", "clcase")
            offset_x (int): X offset for screen shake
            offset_y (int): Y offset for screen shake
        """
        # Update swirl particles
        self._update_swirl_particles()
        
        # Draw swirl particles
        self._draw_swirl_particles(screen, offset_x, offset_y)
        
        # Draw center target
        self._draw_center_target(screen, target_letter, mode, offset_x, offset_y)
        
    def trigger_convergence(self, target_x, target_y):
        """
        Trigger swirl particles to converge toward a target point.
        
        Args:
            target_x (int): X coordinate of convergence target
            target_y (int): Y coordinate of convergence target
        """
        if not self.particles_converging:  # Prevent re-triggering while already converging
            self.particles_converging = True
            self.convergence_target = (target_x, target_y)
            self.convergence_timer = 30  # Duration for convergence (frames)
            
    def _create_swirl_particles(self, radius=None, count=None):
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
                    
    def _draw_swirl_particles(self, screen, offset_x=0, offset_y=0):
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
            
    def _draw_center_target(self, screen, target_letter, mode, offset_x=0, offset_y=0):
        """Draw the center target display using cached fonts for performance."""
        if not target_letter:
            return
            
        # Update color transition
        self._update_color_transition()
        
        # Calculate center position with offset
        center_x = self.player_x + offset_x
        center_y = self.player_y + offset_y
        
        if mode == "shapes":
            # Draw the center target display as a shape outline
            self._draw_shape_target(screen, target_letter, center_x, center_y)
        else:
            # Draw text target for Alphabet, Numbers, C/L Case using cached fonts
            self._draw_text_target_cached(screen, target_letter, mode, center_x, center_y)
            
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
            
    def _get_interpolated_color(self):
        """Get the current interpolated color for the center target."""
        # Interpolate between current and next color
        r = int(self.player_current_color[0] * (1 - self.player_color_transition) + 
                self.player_next_color[0] * self.player_color_transition)
        g = int(self.player_current_color[1] * (1 - self.player_color_transition) + 
                self.player_next_color[1] * self.player_color_transition)
        b = int(self.player_current_color[2] * (1 - self.player_color_transition) + 
                self.player_next_color[2] * self.player_color_transition)
        return (r, g, b)
        
    def _draw_text_target_cached(self, screen, target_letter, mode, center_x, center_y):
        """Draw text-based center target using cached font surfaces for performance."""
        center_target_color = self._get_interpolated_color()
        
        # PERFORMANCE OPTIMIZATION: Use cached font surface if available
        if self.resource_manager:
            try:
                cached_surface = self.resource_manager.get_center_target_surface(mode, target_letter, center_target_color)
                surface_rect = cached_surface.get_rect(center=(center_x, center_y))
                screen.blit(cached_surface, surface_rect)
                return
            except:
                pass  # Fall back to original rendering if cache fails
        
        # Fallback: Original rendering method
        self._draw_text_target_fallback(screen, target_letter, mode, center_x, center_y, center_target_color)
        
    def _draw_text_target_fallback(self, screen, target_letter, mode, center_x, center_y, center_target_color):
        """Fallback text rendering method (original implementation)."""
        display_char = target_letter  # default

        if mode == "clcase":
            display_char = target_letter.upper()
        elif mode == "alphabet" and target_letter == "a":
            display_char = "α"

        player_text = self.player_font.render(display_char, True, center_target_color)
        player_rect = player_text.get_rect(center=(center_x, center_y))
        screen.blit(player_text, player_rect)
        
    def _draw_shape_target(self, screen, target_letter, center_x, center_y):
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


class SoundManager:
    """
    Universal class to manage sound effects and voice announcements.
    Handles pygame mixer initialization, sound loading, and playback.
    """
    
    def __init__(self):
        """
        Initialize the sound manager.
        """
        self.initialized = False
        self.sounds = {}
        self.voice_sounds = {}
        self.master_volume = 0.7
        self.sfx_volume = 0.8
        self.voice_volume = 0.9
        self.muted = False
        self.voice_generator = None  # Will be initialized lazily
        self.event_tracker = None  # Will be set by external code
        
        # Initialize pygame mixer
        self._initialize_mixer()
        
        # Auto-load basic sound effects
        self._load_default_sounds()
        
    def _initialize_mixer(self):
        """Initialize pygame mixer with appropriate settings."""
        try:
            # Check if mixer is already initialized
            if pygame.mixer.get_init():
                print("✅ Sound system already initialized, using existing mixer")
                self.initialized = True
                if self.event_tracker:
                    self.event_tracker.track_initialization("sound_mixer", True, "Using existing mixer")
                return
                
            # Initialize with better settings to avoid static
            pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=1024)
            pygame.mixer.init()
            self.initialized = True
            print("✅ Sound system initialized successfully")
            if self.event_tracker:
                self.event_tracker.track_initialization("sound_mixer", True, "New mixer initialized")
        except pygame.error as e:
            print(f"❌ Failed to initialize sound system: {e}")
            self.initialized = False
            
    def _load_default_sounds(self):
        """Load default sound effects from the sounds directory."""
        if not self.initialized:
            return
            
        import os
        
        # Get the sounds directory path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sounds_dir = os.path.join(current_dir, "sounds")
        
        # Load basic sound effects
        sound_files = {
            "explosion": "explosion.wav",
            "laser": "laser.wav"
        }
        
        for sound_name, filename in sound_files.items():
            file_path = os.path.join(sounds_dir, filename)
            if os.path.exists(file_path):
                self.load_sound(sound_name, file_path)
            else:
                print(f"⚠️ Sound file not found: {file_path}")
        
        # Load all voice sounds for letters, numbers, colors, and shapes
        # Letters A-Z
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        for letter in alphabet:
            file_path = os.path.join(sounds_dir, f"{letter}.wav")
            if os.path.exists(file_path):
                self.load_voice_sound(letter, file_path)
        
        # Numbers 1-10
        numbers = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
        for number in numbers:
            file_path = os.path.join(sounds_dir, f"{number}.wav")
            if os.path.exists(file_path):
                self.load_voice_sound(number, file_path)
        
        # Colors
        colors = ["red", "blue", "green", "yellow", "purple"]
        for color in colors:
            file_path = os.path.join(sounds_dir, f"{color}.wav")
            if os.path.exists(file_path):
                self.load_voice_sound(color, file_path)
        
        # Shapes
        shapes = ["circle", "square", "triangle", "rectangle", "pentagon"]
        for shape in shapes:
            file_path = os.path.join(sounds_dir, f"{shape}.wav")
            if os.path.exists(file_path):
                self.load_voice_sound(shape, file_path)
            
    def reset(self):
        """Reset sound manager state for new level/game."""
        # Stop all currently playing sounds
        if self.initialized:
            pygame.mixer.stop()
            
    def load_sound(self, sound_name, file_path):
        """
        Load a sound effect from file.
        
        Args:
            sound_name (str): Internal name for the sound
            file_path (str): Path to the sound file
            
        Returns:
            bool: True if loaded successfully, False otherwise
        """
        if not self.initialized:
            print(f"⚠️ Sound system not initialized, cannot load {sound_name}")
            return False
            
        try:
            import os
            if not os.path.exists(file_path):
                print(f"❌ Sound file not found: {file_path}")
                return False
                
            sound = pygame.mixer.Sound(file_path)
            # Ensure volume doesn't clip by limiting it
            volume = min(0.8, self.sfx_volume * self.master_volume)
            sound.set_volume(volume)
            self.sounds[sound_name] = sound
            print(f"✅ Loaded sound: {sound_name} (volume: {volume:.2f})")
            return True
        except pygame.error as e:
            print(f"❌ Failed to load sound {sound_name}: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error loading sound {sound_name}: {e}")
            return False
            
    def load_voice_sound(self, voice_name, file_path):
        """
        Load a voice announcement from file.
        
        Args:
            voice_name (str): Internal name for the voice sound
            file_path (str): Path to the voice file
            
        Returns:
            bool: True if loaded successfully, False otherwise
        """
        if not self.initialized:
            print(f"⚠️ Sound system not initialized, cannot load voice {voice_name}")
            return False
            
        try:
            import os
            if not os.path.exists(file_path):
                print(f"❌ Voice file not found: {file_path}")
                return False
                
            sound = pygame.mixer.Sound(file_path)
            # Ensure volume doesn't clip by limiting it
            volume = min(0.9, self.voice_volume * self.master_volume)
            sound.set_volume(volume)
            self.voice_sounds[voice_name] = sound
            print(f"✅ Loaded voice: {voice_name} (volume: {volume:.2f})")
            return True
        except pygame.error as e:
            print(f"❌ Failed to load voice {voice_name}: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error loading voice {voice_name}: {e}")
            return False
            
    def play_sound(self, sound_name):
        """
        Play a sound effect.
        
        Args:
            sound_name (str): Name of the sound to play
            
        Returns:
            bool: True if played successfully, False otherwise
        """
        if not self.initialized or self.muted:
            return False
            
        if sound_name not in self.sounds:
            print(f"⚠️ Sound '{sound_name}' not found in loaded sounds")
            return False
            
        try:
            # Stop the sound first to prevent overlapping static
            self.sounds[sound_name].stop()
            # Play the sound
            self.sounds[sound_name].play()
            
            # Track successful sound play
            if self.event_tracker:
                self.event_tracker.track_sound_played(sound_name, True)
            
            return True
        except pygame.error as e:
            print(f"❌ Failed to play sound {sound_name}: {e}")
            return False
            
    def play_voice(self, voice_name):
        """
        Play a voice announcement.
        
        Args:
            voice_name (str): Name of the voice to play
            
        Returns:
            bool: True if played successfully, False otherwise
        """
        if not self.initialized or self.muted:
            return False
            
        # Ensure voice is available, generate if needed
        if voice_name not in self.voice_sounds:
            print(f"🔄 Voice '{voice_name}' not loaded, attempting to generate...")
            if not self.ensure_voice_available(voice_name):
                print(f"❌ Failed to ensure voice '{voice_name}' is available")
                return False
            
        try:
            # Stop only voice sounds to prevent overlap, but don't stop all sounds
            # Instead of stopping everything, let's just play the voice
            channel = self.voice_sounds[voice_name].play()
            print(f"🔊 Playing voice: {voice_name}")
            
            if channel is None:
                print(f"⚠️ No available channel to play voice: {voice_name}")
                return False
            
            # Track successful voice play
            if self.event_tracker:
                self.event_tracker.track_voice_played(voice_name, True)
            
            return True
        except pygame.error as e:
            print(f"❌ Failed to play voice {voice_name}: {e}")
            return False
            
    def set_master_volume(self, volume):
        """
        Set master volume (0.0 to 1.0).
        
        Args:
            volume (float): Volume level between 0.0 and 1.0
        """
        self.master_volume = max(0.0, min(1.0, volume))
        self._update_all_volumes()
        
    def set_sfx_volume(self, volume):
        """
        Set sound effects volume (0.0 to 1.0).
        
        Args:
            volume (float): Volume level between 0.0 and 1.0
        """
        self.sfx_volume = max(0.0, min(1.0, volume))
        self._update_sfx_volumes()
        
    def set_voice_volume(self, volume):
        """
        Set voice announcement volume (0.0 to 1.0).
        
        Args:
            volume (float): Volume level between 0.0 and 1.0
        """
        self.voice_volume = max(0.0, min(1.0, volume))
        self._update_voice_volumes()
        
    def toggle_mute(self):
        """Toggle mute state for all sounds."""
        self.muted = not self.muted
        if self.muted:
            pygame.mixer.set_num_channels(0)
        else:
            pygame.mixer.set_num_channels(8)  # Default number of channels
            
    def _update_all_volumes(self):
        """Update volumes for all loaded sounds."""
        self._update_sfx_volumes()
        self._update_voice_volumes()
        
    def _update_sfx_volumes(self):
        """Update volumes for all sound effects."""
        for sound in self.sounds.values():
            sound.set_volume(self.sfx_volume * self.master_volume)
            
    def _update_voice_volumes(self):
        """Update volumes for all voice sounds."""
        for sound in self.voice_sounds.values():
            sound.set_volume(self.voice_volume * self.master_volume)
    
    def _get_voice_generator(self):
        """Lazy initialization of voice generator."""
        if self.voice_generator is None:
            try:
                from utils.voice_generator import UniversalVoiceGenerator
                self.voice_generator = UniversalVoiceGenerator()
            except ImportError:
                print("⚠️ VoiceGenerator not available, voice generation disabled")
                self.voice_generator = False  # Mark as unavailable
        return self.voice_generator if self.voice_generator else None
    
    def generate_and_load_voice(self, text):
        """
        Generate a voice file using AI and load it.
        
        Args:
            text (str): Text to generate voice for
            
        Returns:
            bool: True if generated and loaded successfully
        """
        voice_gen = self._get_voice_generator()
        if not voice_gen:
            return False
            
        try:
            import os
            sounds_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sounds")
            file_path = os.path.join(sounds_dir, f"{text}.wav")
            
            # Generate the voice file
            if voice_gen.generate_voice_file(text, file_path):
                # Load the generated file
                return self.load_voice_sound(text, file_path)
            else:
                print(f"⚠️ Failed to generate voice for: {text}")
                return False
        except Exception as e:
            print(f"❌ Error generating voice for {text}: {e}")
            return False
    
    def ensure_voice_available(self, text):
        """
        Ensure a voice is available, generating it if necessary.
        
        Args:
            text (str): Text to ensure voice for
            
        Returns:
            bool: True if voice is available
        """
        # Check if already loaded
        if text in self.voice_sounds:
            return True
            
        # Try to load from existing file
        import os
        sounds_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sounds")
        file_path = os.path.join(sounds_dir, f"{text}.wav")
        
        if os.path.exists(file_path):
            return self.load_voice_sound(text, file_path)
        else:
            # Generate and load the voice
            return self.generate_and_load_voice(text)
            
    def set_event_tracker(self, event_tracker):
        """Set the event tracker for this sound manager."""
        self.event_tracker = event_tracker
    
    def get_status(self):
        """
        Get current status of the sound manager.
        
        Returns:
            dict: Status information
        """
        return {
            "initialized": self.initialized,
            "muted": self.muted,
            "master_volume": self.master_volume,
            "sfx_volume": self.sfx_volume,
            "voice_volume": self.voice_volume,
            "loaded_sounds": len(self.sounds),
            "loaded_voices": len(self.voice_sounds)
        }