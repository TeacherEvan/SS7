"""
Comprehensive Event Tracking System for SS6 Super Student Game

This module provides individual event trackers to monitor all game processes:
- Sound events (play, fail, generate)
- Hit events (target destroyed, missed)
- Level transitions (start, complete, exit)
- Performance metrics (FPS, memory usage)
- Input events (mouse, touch, keyboard)
- System events (errors, warnings)

Classes:
- EventTracker: Base class for all event trackers
- SoundEventTracker: Tracks sound-related events
- GameplayEventTracker: Tracks gameplay events (hits, misses, scores)
- PerformanceTracker: Monitors performance metrics
- LevelEventTracker: Tracks level progression and transitions
- InputEventTracker: Monitors input events
- SystemEventTracker: Tracks system events and errors
- EventManager: Centralized manager for all event trackers
"""

import json
import os
import threading
import time
from collections import defaultdict, deque
from datetime import datetime
from typing import Any, Dict, List, Optional

import psutil


class EventTracker:
    """Base class for all event trackers."""

    def __init__(self, name: str, max_events: int = 1000):
        """
        Initialize the event tracker.

        Args:
            name (str): Name of the tracker
            max_events (int): Maximum number of events to keep in memory
        """
        self.name = name
        self.events = deque(maxlen=max_events)
        self.start_time = time.time()
        self.enabled = True
        self.lock = threading.Lock()

    def track_event(self, event_type: str, data: Dict[str, Any] = None):
        """
        Track an event.

        Args:
            event_type (str): Type of event
            data (dict): Additional event data
        """
        if not self.enabled:
            return

        with self.lock:
            event = {
                "timestamp": time.time(),
                "datetime": datetime.now().isoformat(),
                "type": event_type,
                "tracker": self.name,
                "data": data or {},
            }
            self.events.append(event)

    def get_events(self, event_type: str = None, limit: int = None) -> List[Dict]:
        """
        Get tracked events.

        Args:
            event_type (str): Filter by event type
            limit (int): Limit number of events returned

        Returns:
            List of events
        """
        with self.lock:
            events = list(self.events)

        if event_type:
            events = [e for e in events if e["type"] == event_type]

        if limit:
            events = events[-limit:]

        return events

    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics for this tracker."""
        with self.lock:
            events = list(self.events)

        if not events:
            return {"total_events": 0, "event_types": {}}

        event_types = defaultdict(int)
        for event in events:
            event_types[event["type"]] += 1

        return {
            "total_events": len(events),
            "event_types": dict(event_types),
            "first_event": events[0]["datetime"] if events else None,
            "last_event": events[-1]["datetime"] if events else None,
            "tracker_name": self.name,
            "enabled": self.enabled,
        }

    def clear_events(self):
        """Clear all tracked events."""
        with self.lock:
            self.events.clear()

    def enable(self):
        """Enable event tracking."""
        self.enabled = True

    def disable(self):
        """Disable event tracking."""
        self.enabled = False


class SoundEventTracker(EventTracker):
    """Tracks sound-related events."""

    def __init__(self):
        super().__init__("SoundEvents")

    def track_sound_played(self, sound_name: str, success: bool = True):
        """Track a sound play event."""
        self.track_event("sound_played", {"sound_name": sound_name, "success": success})

    def track_voice_played(self, voice_name: str, success: bool = True):
        """Track a voice play event."""
        self.track_event("voice_played", {"voice_name": voice_name, "success": success})

    def track_voice_generated(self, text: str, success: bool = True, generation_time: float = None):
        """Track a voice generation event."""
        self.track_event(
            "voice_generated",
            {"text": text, "success": success, "generation_time": generation_time},
        )

    def track_sound_error(self, error_type: str, details: str):
        """Track a sound system error."""
        self.track_event("sound_error", {"error_type": error_type, "details": details})

    def get_sound_stats(self) -> Dict[str, Any]:
        """Get sound-specific statistics."""
        events = self.get_events()

        sounds_played = defaultdict(int)
        voices_played = defaultdict(int)
        voices_generated = defaultdict(int)
        errors = 0

        for event in events:
            if event["type"] == "sound_played":
                sounds_played[event["data"]["sound_name"]] += 1
            elif event["type"] == "voice_played":
                voices_played[event["data"]["voice_name"]] += 1
            elif event["type"] == "voice_generated":
                voices_generated[event["data"]["text"]] += 1
            elif event["type"] == "sound_error":
                errors += 1

        return {
            "sounds_played": dict(sounds_played),
            "voices_played": dict(voices_played),
            "voices_generated": dict(voices_generated),
            "total_errors": errors,
        }


class GameplayEventTracker(EventTracker):
    """Tracks gameplay events (hits, misses, scores)."""

    def __init__(self):
        super().__init__("GameplayEvents")
        self.session_stats = {
            "targets_hit": 0,
            "targets_missed": 0,
            "total_score": 0,
            "current_streak": 0,
            "best_streak": 0,
        }

    def track_target_hit(self, target_type: str, target_value: str, score_gained: int = 0):
        """Track a successful target hit."""
        self.session_stats["targets_hit"] += 1
        self.session_stats["total_score"] += score_gained
        self.session_stats["current_streak"] += 1

        if self.session_stats["current_streak"] > self.session_stats["best_streak"]:
            self.session_stats["best_streak"] = self.session_stats["current_streak"]

        self.track_event(
            "target_hit",
            {
                "target_type": target_type,
                "target_value": target_value,
                "score_gained": score_gained,
                "current_streak": self.session_stats["current_streak"],
            },
        )

    def track_target_missed(self, click_x: int, click_y: int):
        """Track a missed target (misclick)."""
        self.session_stats["targets_missed"] += 1
        self.session_stats["current_streak"] = 0

        self.track_event(
            "target_missed", {"click_x": click_x, "click_y": click_y, "streak_broken": True}
        )

    def track_ability_used(self, ability_name: str):
        """Track special ability usage."""
        self.track_event("ability_used", {"ability_name": ability_name})

    def track_checkpoint_reached(self, checkpoint_number: int, total_score: int):
        """Track checkpoint reached."""
        self.track_event(
            "checkpoint_reached",
            {"checkpoint_number": checkpoint_number, "total_score": total_score},
        )

    def get_gameplay_stats(self) -> Dict[str, Any]:
        """Get gameplay statistics."""
        accuracy = 0
        if self.session_stats["targets_hit"] + self.session_stats["targets_missed"] > 0:
            accuracy = (
                self.session_stats["targets_hit"]
                / (self.session_stats["targets_hit"] + self.session_stats["targets_missed"])
                * 100
            )

        return {**self.session_stats, "accuracy": round(accuracy, 2)}

    def reset_session_stats(self):
        """Reset session statistics for a new level."""
        self.session_stats = {
            "targets_hit": 0,
            "targets_missed": 0,
            "total_score": 0,
            "current_streak": 0,
            "best_streak": 0,
        }


class PerformanceTracker(EventTracker):
    """Monitors performance metrics."""

    def __init__(self):
        super().__init__(
            "PerformanceMetrics", max_events=500
        )  # Smaller buffer for performance data
        self.process = psutil.Process()
        self.fps_history = deque(maxlen=60)  # Last 60 FPS readings

    def track_frame(self, fps: float):
        """Track frame rate."""
        self.fps_history.append(fps)

        # Only track detailed performance every 10 frames to reduce overhead
        if len(self.fps_history) % 10 == 0:
            try:
                memory_info = self.process.memory_info()
                cpu_percent = self.process.cpu_percent()

                self.track_event(
                    "performance_sample",
                    {
                        "fps": fps,
                        "memory_mb": memory_info.rss / 1024 / 1024,
                        "cpu_percent": cpu_percent,
                        "avg_fps_10": sum(list(self.fps_history)[-10:])
                        / min(len(self.fps_history), 10),
                    },
                )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass  # Process monitoring not available

    def track_memory_usage(self):
        """Track current memory usage."""
        try:
            memory_info = self.process.memory_info()
            self.track_event(
                "memory_usage",
                {"rss_mb": memory_info.rss / 1024 / 1024, "vms_mb": memory_info.vms / 1024 / 1024},
            )
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        if not self.fps_history:
            return {"fps": {"current": 0, "avg": 0, "min": 0, "max": 0}}

        fps_list = list(self.fps_history)

        try:
            memory_info = self.process.memory_info()
            current_memory = memory_info.rss / 1024 / 1024
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            current_memory = 0

        return {
            "fps": {
                "current": fps_list[-1] if fps_list else 0,
                "avg": sum(fps_list) / len(fps_list),
                "min": min(fps_list),
                "max": max(fps_list),
            },
            "memory_mb": current_memory,
            "frame_count": len(fps_list),
        }


class LevelEventTracker(EventTracker):
    """Tracks level progression and transitions."""

    def __init__(self):
        super().__init__("LevelEvents")
        self.current_level = None
        self.level_start_time = None

    def track_level_start(self, level_name: str):
        """Track level start."""
        self.current_level = level_name
        self.level_start_time = time.time()

        self.track_event("level_start", {"level_name": level_name})

    def track_level_complete(
        self, level_name: str, final_score: int, completion_time: float = None
    ):
        """Track level completion."""
        if not completion_time and self.level_start_time:
            completion_time = time.time() - self.level_start_time

        self.track_event(
            "level_complete",
            {
                "level_name": level_name,
                "final_score": final_score,
                "completion_time": completion_time,
            },
        )

        self.current_level = None
        self.level_start_time = None

    def track_level_exit(self, level_name: str, reason: str = "user_exit"):
        """Track level exit (ESC, quit, etc.)."""
        completion_time = None
        if self.level_start_time:
            completion_time = time.time() - self.level_start_time

        self.track_event(
            "level_exit",
            {"level_name": level_name, "reason": reason, "time_played": completion_time},
        )

        self.current_level = None
        self.level_start_time = None

    def track_group_complete(self, level_name: str, group_number: int, items_in_group: List[str]):
        """Track completion of a group within a level."""
        self.track_event(
            "group_complete",
            {
                "level_name": level_name,
                "group_number": group_number,
                "items_in_group": items_in_group,
            },
        )


class InputEventTracker(EventTracker):
    """Monitors input events."""

    def __init__(self):
        super().__init__("InputEvents")

    def track_mouse_click(self, x: int, y: int, button: int):
        """Track mouse click."""
        self.track_event("mouse_click", {"x": x, "y": y, "button": button})

    def track_touch_event(self, touch_id: int, x: int, y: int, event_type: str):
        """Track touch event."""
        self.track_event(
            "touch_event",
            {"touch_id": touch_id, "x": x, "y": y, "event_type": event_type},  # down, up, motion
        )

    def track_key_press(self, key: str):
        """Track key press."""
        self.track_event("key_press", {"key": key})


class SystemEventTracker(EventTracker):
    """Tracks system events and errors."""

    def __init__(self):
        super().__init__("SystemEvents")

    def track_error(self, error_type: str, message: str, details: Dict[str, Any] = None):
        """Track system error."""
        self.track_event(
            "error", {"error_type": error_type, "message": message, "details": details or {}}
        )

    def track_warning(self, warning_type: str, message: str):
        """Track system warning."""
        self.track_event("warning", {"warning_type": warning_type, "message": message})

    def track_initialization(self, component: str, success: bool, details: str = None):
        """Track component initialization."""
        self.track_event(
            "initialization", {"component": component, "success": success, "details": details}
        )


class EventManager:
    """Centralized manager for all event trackers."""

    def __init__(self):
        """Initialize the event manager with all trackers."""
        self.trackers = {
            "sound": SoundEventTracker(),
            "gameplay": GameplayEventTracker(),
            "performance": PerformanceTracker(),
            "level": LevelEventTracker(),
            "input": InputEventTracker(),
            "system": SystemEventTracker(),
        }
        self.enabled = True

    def get_tracker(self, tracker_name: str) -> Optional[EventTracker]:
        """Get a specific tracker by name."""
        return self.trackers.get(tracker_name)

    def track_event(self, tracker_name: str, event_type: str, data: Dict[str, Any] = None):
        """Track an event using a specific tracker."""
        if not self.enabled:
            return

        tracker = self.get_tracker(tracker_name)
        if tracker:
            tracker.track_event(event_type, data)

    def get_all_summaries(self) -> Dict[str, Any]:
        """Get summaries from all trackers."""
        summaries = {}
        for name, tracker in self.trackers.items():
            summaries[name] = tracker.get_summary()
        return summaries

    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics from all trackers."""
        stats = {
            "sound": self.trackers["sound"].get_sound_stats(),
            "gameplay": self.trackers["gameplay"].get_gameplay_stats(),
            "performance": self.trackers["performance"].get_performance_stats(),
            "summaries": self.get_all_summaries(),
        }
        return stats

    def export_events(self, file_path: str, tracker_names: List[str] = None):
        """
        Export events to a JSON file.

        Args:
            file_path (str): Path to export file
            tracker_names (List[str]): Specific trackers to export (None for all)
        """
        if tracker_names is None:
            tracker_names = list(self.trackers.keys())

        export_data = {"export_timestamp": datetime.now().isoformat(), "trackers": {}}

        for tracker_name in tracker_names:
            if tracker_name in self.trackers:
                tracker = self.trackers[tracker_name]
                export_data["trackers"][tracker_name] = {
                    "summary": tracker.get_summary(),
                    "events": tracker.get_events(),
                }

        try:
            with open(file_path, "w") as f:
                json.dump(export_data, f, indent=2)
            return True
        except Exception as e:
            self.track_event(
                "system",
                "error",
                {"error_type": "export_failed", "message": str(e), "file_path": file_path},
            )
            return False

    def clear_all_events(self):
        """Clear events from all trackers."""
        for tracker in self.trackers.values():
            tracker.clear_events()

    def enable_all(self):
        """Enable all trackers."""
        self.enabled = True
        for tracker in self.trackers.values():
            tracker.enable()

    def disable_all(self):
        """Disable all trackers."""
        self.enabled = False
        for tracker in self.trackers.values():
            tracker.disable()

    def reset_gameplay_stats(self):
        """Reset gameplay statistics for a new level."""
        if "gameplay" in self.trackers:
            self.trackers["gameplay"].reset_session_stats()


# Global event manager instance
event_manager = EventManager()


def get_event_manager() -> EventManager:
    """Get the global event manager instance."""
    return event_manager
