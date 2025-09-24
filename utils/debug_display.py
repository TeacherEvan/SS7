"""
Debug Event Display for SS6 Super Student Game

This module provides a debug overlay to display real-time event tracking statistics
during gameplay. Press F1 to toggle the debug display.

Features:
- Performance metrics (FPS, memory usage)
- Gameplay statistics (hits, misses, accuracy)
- Sound events (sounds played, voices generated)
- Level progression tracking
- Real-time event stream

Usage:
    from utils.debug_display import DebugDisplay
    debug = DebugDisplay(screen, font)
    debug.update(event_manager)
    debug.draw()
"""

import pygame
from typing import Dict, Any, Optional


class DebugDisplay:
    """Debug overlay for displaying event tracking statistics."""
    
    def __init__(self, screen: pygame.Surface, font: pygame.font.Font):
        """
        Initialize the debug display.
        
        Args:
            screen: Pygame screen surface
            font: Font for rendering text
        """
        self.screen = screen
        self.font = font
        self.enabled = False
        self.stats = {}
        self.last_update = 0
        self.background_color = (0, 0, 0, 180)  # Semi-transparent black
        self.text_color = (255, 255, 255)
        self.highlight_color = (255, 255, 0)
        
    def toggle(self):
        """Toggle debug display visibility."""
        self.enabled = not self.enabled
        
    def update(self, event_manager):
        """
        Update debug statistics from event manager.
        
        Args:
            event_manager: The event manager instance
        """
        if not self.enabled:
            return
            
        import time
        current_time = time.time()
        
        # Update every 0.5 seconds to avoid performance impact
        if current_time - self.last_update < 0.5:
            return
            
        self.last_update = current_time
        
        try:
            self.stats = event_manager.get_comprehensive_stats()
        except Exception as e:
            self.stats = {"error": str(e)}
    
    def draw(self):
        """Draw the debug overlay on screen."""
        if not self.enabled or not self.stats:
            return
            
        # Calculate overlay dimensions
        overlay_width = 350
        overlay_height = 400
        x = self.screen.get_width() - overlay_width - 10
        y = 10
        
        # Create semi-transparent overlay surface
        overlay = pygame.Surface((overlay_width, overlay_height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        
        # Draw border
        pygame.draw.rect(overlay, (100, 100, 100), (0, 0, overlay_width, overlay_height), 2)
        
        # Draw title
        title_text = self.font.render("DEBUG - Event Tracking", True, self.highlight_color)
        overlay.blit(title_text, (10, 10))
        
        # Draw statistics
        y_offset = 40
        line_height = 20
        
        # Performance stats
        if "performance" in self.stats:
            perf = self.stats["performance"]
            fps_data = perf.get("fps", {})
            
            self._draw_text(overlay, f"=== PERFORMANCE ===", 10, y_offset, self.highlight_color)
            y_offset += line_height
            
            self._draw_text(overlay, f"Current FPS: {fps_data.get('current', 0):.1f}", 15, y_offset)
            y_offset += line_height
            
            self._draw_text(overlay, f"Average FPS: {fps_data.get('avg', 0):.1f}", 15, y_offset)
            y_offset += line_height
            
            self._draw_text(overlay, f"Memory: {perf.get('memory_mb', 0):.1f} MB", 15, y_offset)
            y_offset += line_height + 5
        
        # Gameplay stats
        if "gameplay" in self.stats:
            gameplay = self.stats["gameplay"]
            
            self._draw_text(overlay, f"=== GAMEPLAY ===", 10, y_offset, self.highlight_color)
            y_offset += line_height
            
            self._draw_text(overlay, f"Targets Hit: {gameplay.get('targets_hit', 0)}", 15, y_offset)
            y_offset += line_height
            
            self._draw_text(overlay, f"Targets Missed: {gameplay.get('targets_missed', 0)}", 15, y_offset)
            y_offset += line_height
            
            self._draw_text(overlay, f"Accuracy: {gameplay.get('accuracy', 0):.1f}%", 15, y_offset)
            y_offset += line_height
            
            self._draw_text(overlay, f"Current Streak: {gameplay.get('current_streak', 0)}", 15, y_offset)
            y_offset += line_height
            
            self._draw_text(overlay, f"Best Streak: {gameplay.get('best_streak', 0)}", 15, y_offset)
            y_offset += line_height + 5
        
        # Sound stats
        if "sound" in self.stats:
            sound = self.stats["sound"]
            
            self._draw_text(overlay, f"=== SOUND ===", 10, y_offset, self.highlight_color)
            y_offset += line_height
            
            voices_played = sound.get("voices_played", {})
            total_voices = sum(voices_played.values())
            self._draw_text(overlay, f"Voices Played: {total_voices}", 15, y_offset)
            y_offset += line_height
            
            voices_generated = sound.get("voices_generated", {})
            total_generated = sum(voices_generated.values())
            self._draw_text(overlay, f"Voices Generated: {total_generated}", 15, y_offset)
            y_offset += line_height
            
            self._draw_text(overlay, f"Sound Errors: {sound.get('total_errors', 0)}", 15, y_offset)
            y_offset += line_height + 5
        
        # Summary stats
        if "summaries" in self.stats:
            summaries = self.stats["summaries"]
            
            self._draw_text(overlay, f"=== EVENT COUNTS ===", 10, y_offset, self.highlight_color)
            y_offset += line_height
            
            for tracker_name, summary in summaries.items():
                if "total_events" in summary:
                    self._draw_text(overlay, f"{tracker_name}: {summary['total_events']}", 15, y_offset)
                    y_offset += line_height
        
        # Add instructions
        y_offset += 10
        self._draw_text(overlay, "Press F1 to toggle", 10, y_offset, (150, 150, 150))
        
        # Blit overlay to main screen
        self.screen.blit(overlay, (x, y))
    
    def _draw_text(self, surface: pygame.Surface, text: str, x: int, y: int, color: tuple = None):
        """Helper method to draw text on a surface."""
        if color is None:
            color = self.text_color
            
        try:
            text_surface = self.font.render(text, True, color)
            surface.blit(text_surface, (x, y))
        except Exception:
            # Fallback for rendering issues
            pass
    
    def handle_event(self, event: pygame.event.Event):
        """
        Handle pygame events for debug display.
        
        Args:
            event: Pygame event
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F1:
                self.toggle()
                return True  # Event handled
        return False