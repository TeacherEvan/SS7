"""
Memory Profiler for SS6 Super Student Game
Monitors memory usage and performance metrics.
"""

import gc
import json
import time
from collections import deque
from pathlib import Path
from typing import Any, Dict, List, Optional

import psutil
import pygame


class PerformanceMetrics:
    """Container for performance metrics."""

    def __init__(self):
        self.fps = 0.0
        self.frame_time = 0.0
        self.memory_usage = 0.0
        self.memory_peak = 0.0
        self.particle_count = 0
        self.object_pool_stats = {}
        self.surface_count = 0
        self.texture_memory = 0.0
        self.gc_count = 0
        self.timestamp = time.time()


class MemoryProfiler:
    """
    Memory and performance profiler for the game.
    """

    def __init__(self, max_history: int = 300):  # 5 minutes at 60 FPS
        """
        Initialize memory profiler.

        Args:
            max_history: Maximum number of metrics to keep in history
        """
        self.max_history = max_history
        self.metrics_history: deque[PerformanceMetrics] = deque(maxlen=max_history)
        self.process = psutil.Process()
        self.start_time = time.time()
        self.frame_count = 0
        self.last_gc_count = 0

        # Performance thresholds
        self.fps_threshold = 30.0  # Minimum acceptable FPS
        self.memory_threshold = 500.0  # MB
        self.frame_time_threshold = 33.33  # ms (30 FPS)

        # Monitoring flags
        self.enabled = True
        self.log_warnings = True
        self.auto_gc = True

    def update(self, dt: float, additional_data: Dict[str, Any] = None):
        """
        Update performance metrics.

        Args:
            dt: Delta time for current frame
            additional_data: Additional metrics to track
        """
        if not self.enabled:
            return

        self.frame_count += 1

        # Create new metrics
        metrics = PerformanceMetrics()

        # Basic timing metrics
        metrics.fps = 1.0 / dt if dt > 0 else 0.0
        metrics.frame_time = dt * 1000.0  # Convert to milliseconds

        # Memory metrics
        memory_info = self.process.memory_info()
        metrics.memory_usage = memory_info.rss / 1024 / 1024  # MB
        metrics.memory_peak = (
            self.process.memory_info().peak_wss / 1024 / 1024
            if hasattr(self.process.memory_info(), "peak_wss")
            else metrics.memory_usage
        )

        # Garbage collection
        gc_count = len(gc.get_objects())
        metrics.gc_count = gc_count

        # Pygame surface tracking
        metrics.surface_count = self._count_pygame_surfaces()
        metrics.texture_memory = self._estimate_texture_memory()

        # Additional data from game
        if additional_data:
            if "particle_count" in additional_data:
                metrics.particle_count = additional_data["particle_count"]
            if "object_pool_stats" in additional_data:
                metrics.object_pool_stats = additional_data["object_pool_stats"]

        # Add to history
        self.metrics_history.append(metrics)

        # Check for performance issues
        if self.log_warnings:
            self._check_performance_warnings(metrics)

        # Auto garbage collection if enabled
        if self.auto_gc and self.frame_count % 300 == 0:  # Every 5 seconds at 60 FPS
            collected = gc.collect()
            if collected > 0:
                print(f"GC: Collected {collected} objects")

    def _count_pygame_surfaces(self) -> int:
        """Count pygame Surface objects in memory."""
        count = 0
        for obj in gc.get_objects():
            if isinstance(obj, pygame.Surface):
                count += 1
        return count

    def _estimate_texture_memory(self) -> float:
        """Estimate memory used by pygame surfaces (in MB)."""
        total_bytes = 0
        for obj in gc.get_objects():
            if isinstance(obj, pygame.Surface):
                # Estimate bytes per pixel based on bit depth
                bytes_per_pixel = obj.get_bitsize() / 8
                surface_bytes = obj.get_width() * obj.get_height() * bytes_per_pixel
                total_bytes += surface_bytes
        return total_bytes / 1024 / 1024  # Convert to MB

    def _check_performance_warnings(self, metrics: PerformanceMetrics):
        """Check for performance issues and log warnings."""
        # FPS warning
        if metrics.fps < self.fps_threshold:
            print(f"Performance Warning: Low FPS ({metrics.fps:.1f})")

        # Memory warning
        if metrics.memory_usage > self.memory_threshold:
            print(f"Memory Warning: High memory usage ({metrics.memory_usage:.1f} MB)")

        # Frame time warning
        if metrics.frame_time > self.frame_time_threshold:
            print(f"Performance Warning: High frame time ({metrics.frame_time:.1f} ms)")

        # Surface count warning
        if metrics.surface_count > 1000:
            print(f"Memory Warning: High surface count ({metrics.surface_count})")

    def get_current_metrics(self) -> Optional[PerformanceMetrics]:
        """Get the most recent metrics."""
        return self.metrics_history[-1] if self.metrics_history else None

    def get_average_metrics(self, samples: int = 60) -> Dict[str, float]:
        """
        Get average metrics over the last N samples.

        Args:
            samples: Number of recent samples to average
        """
        if not self.metrics_history:
            return {}

        recent_metrics = list(self.metrics_history)[-samples:]

        if not recent_metrics:
            return {}

        return {
            "avg_fps": sum(m.fps for m in recent_metrics) / len(recent_metrics),
            "avg_frame_time": sum(m.frame_time for m in recent_metrics) / len(recent_metrics),
            "avg_memory": sum(m.memory_usage for m in recent_metrics) / len(recent_metrics),
            "max_memory": max(m.memory_usage for m in recent_metrics),
            "avg_surface_count": sum(m.surface_count for m in recent_metrics) / len(recent_metrics),
            "avg_texture_memory": sum(m.texture_memory for m in recent_metrics)
            / len(recent_metrics),
        }

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary."""
        if not self.metrics_history:
            return {}

        current = self.metrics_history[-1]
        avg_60 = self.get_average_metrics(60)
        runtime = time.time() - self.start_time

        return {
            "runtime_seconds": runtime,
            "total_frames": self.frame_count,
            "current": {
                "fps": current.fps,
                "frame_time_ms": current.frame_time,
                "memory_mb": current.memory_usage,
                "surface_count": current.surface_count,
                "texture_memory_mb": current.texture_memory,
                "particle_count": current.particle_count,
            },
            "averages_60s": avg_60,
            "peak_memory_mb": max(m.memory_usage for m in self.metrics_history),
            "min_fps": min(m.fps for m in self.metrics_history),
            "max_frame_time_ms": max(m.frame_time for m in self.metrics_history),
        }

    def export_metrics(self, filepath: str, include_history: bool = False):
        """
        Export metrics to JSON file.

        Args:
            filepath: Path to save metrics
            include_history: Whether to include full history or just summary
        """
        data = {
            "summary": self.get_performance_summary(),
            "config": {
                "fps_threshold": self.fps_threshold,
                "memory_threshold": self.memory_threshold,
                "frame_time_threshold": self.frame_time_threshold,
            },
        }

        if include_history:
            data["history"] = [
                {
                    "timestamp": m.timestamp,
                    "fps": m.fps,
                    "frame_time_ms": m.frame_time,
                    "memory_mb": m.memory_usage,
                    "surface_count": m.surface_count,
                    "texture_memory_mb": m.texture_memory,
                    "particle_count": m.particle_count,
                    "object_pool_stats": m.object_pool_stats,
                }
                for m in self.metrics_history
            ]

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    def draw_overlay(
        self, screen: pygame.Surface, font: pygame.font.Font, x: int = 10, y: int = 10
    ):
        """
        Draw performance overlay on screen.

        Args:
            screen: Surface to draw on
            font: Font to use for text
            x, y: Position to draw overlay
        """
        if not self.enabled or not self.metrics_history:
            return

        current = self.metrics_history[-1]
        avg_metrics = self.get_average_metrics(60)

        # Prepare text lines
        lines = [
            f"FPS: {current.fps:.1f} (avg: {avg_metrics.get('avg_fps', 0):.1f})",
            f"Frame: {current.frame_time:.1f}ms",
            f"Memory: {current.memory_usage:.1f}MB",
            f"Surfaces: {current.surface_count}",
            f"Tex Mem: {current.texture_memory:.1f}MB",
            f"Particles: {current.particle_count}",
        ]

        # Add object pool stats if available
        if current.object_pool_stats:
            for pool_name, stats in current.object_pool_stats.items():
                lines.append(f"{pool_name}: {stats.get('in_use', 0)}/{stats.get('total', 0)}")

        # Draw background
        line_height = font.get_height() + 2
        bg_height = len(lines) * line_height + 10
        bg_rect = pygame.Rect(x - 5, y - 5, 250, bg_height)
        pygame.draw.rect(screen, (0, 0, 0, 128), bg_rect)
        pygame.draw.rect(screen, (255, 255, 255), bg_rect, 1)

        # Draw text lines
        for i, line in enumerate(lines):
            # Choose color based on performance
            color = (255, 255, 255)  # White default
            if "FPS:" in line and current.fps < self.fps_threshold:
                color = (255, 100, 100)  # Red for low FPS
            elif "Memory:" in line and current.memory_usage > self.memory_threshold:
                color = (255, 255, 100)  # Yellow for high memory
            elif "Frame:" in line and current.frame_time > self.frame_time_threshold:
                color = (255, 100, 100)  # Red for high frame time

            text_surface = font.render(line, True, color)
            screen.blit(text_surface, (x, y + i * line_height))

    def toggle_enabled(self):
        """Toggle profiler enabled state."""
        self.enabled = not self.enabled
        print(f"Memory Profiler: {'Enabled' if self.enabled else 'Disabled'}")

    def force_gc(self) -> int:
        """Force garbage collection and return number of objects collected."""
        return gc.collect()

    def clear_history(self):
        """Clear metrics history."""
        self.metrics_history.clear()
        print("Memory Profiler: History cleared")


# Global profiler instance
memory_profiler = MemoryProfiler()


def get_memory_profiler() -> MemoryProfiler:
    """Get the global memory profiler instance."""
    return memory_profiler
