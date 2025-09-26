#!/usr/bin/env python3
"""
Sound System Audit Tool for SS6 Super Student Game
Comprehensive analysis of all audio files for quality, consistency, and integration.
"""

import json
import os
import statistics
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pygame


class SoundAuditor:
    """Comprehensive sound system auditor for SS6 game."""

    def __init__(self, sounds_dir: str = "sounds"):
        """Initialize the sound auditor."""
        self.sounds_dir = Path(sounds_dir)
        self.results = {
            "total_files": 0,
            "categories": {},
            "quality_metrics": {},
            "issues": [],
            "recommendations": [],
        }

        # Initialize pygame for audio analysis
        os.environ["SDL_AUDIODRIVER"] = "dummy"  # Headless mode
        pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=1024)
        pygame.mixer.init()

        # Expected file categories for educational game
        self.categories = {
            "uppercase_letters": [f"{chr(65+i)}.wav" for i in range(26)],  # A-Z
            "lowercase_letters": [f"{chr(97+i)}.wav" for i in range(26)],  # a-z
            "numbers": [f"{i}.wav" for i in range(1, 11)],  # 1-10
            "colors": ["red.wav", "blue.wav", "green.wav", "yellow.wav", "purple.wav"],
            "shapes": ["circle.wav", "square.wav", "triangle.wav", "rectangle.wav", "pentagon.wav"],
            "effects": ["explosion.wav", "laser.wav"],
        }

    def analyze_all_sounds(self) -> Dict:
        """Perform comprehensive analysis of all sound files."""
        print("🔊 Starting comprehensive sound system audit...")
        print("=" * 60)

        # Get all WAV files
        sound_files = list(self.sounds_dir.glob("*.wav"))
        self.results["total_files"] = len(sound_files)

        print(f"📁 Found {len(sound_files)} audio files")

        # Analyze each category
        for category, expected_files in self.categories.items():
            print(f"\n📂 Analyzing {category}...")
            self.results["categories"][category] = self._analyze_category(expected_files)

        # Overall quality metrics
        self._calculate_overall_metrics()

        # Generate recommendations
        self._generate_recommendations()

        return self.results

    def _analyze_category(self, expected_files: List[str]) -> Dict:
        """Analyze a specific category of sound files."""
        category_data = {
            "expected_count": len(expected_files),
            "found_count": 0,
            "missing_files": [],
            "file_details": {},
            "duration_stats": {},
            "quality_issues": [],
        }

        durations = []
        volumes = []

        for filename in expected_files:
            file_path = self.sounds_dir / filename

            if file_path.exists():
                category_data["found_count"] += 1

                try:
                    # Load and analyze the sound
                    sound = pygame.mixer.Sound(str(file_path))
                    duration = sound.get_length()
                    durations.append(duration)

                    # Get file size for quality indication
                    file_size = file_path.stat().st_size

                    # Store file details
                    category_data["file_details"][filename] = {
                        "duration": round(duration, 2),
                        "file_size": file_size,
                        "size_kb": round(file_size / 1024, 1),
                        "quality_rating": self._assess_quality(duration, file_size),
                    }

                    # Check for quality issues
                    if duration < 0.5:
                        category_data["quality_issues"].append(
                            f"{filename}: Too short ({duration:.2f}s)"
                        )
                    elif duration > 2.0:
                        category_data["quality_issues"].append(
                            f"{filename}: Too long ({duration:.2f}s)"
                        )

                    if file_size < 30000:  # Less than 30KB
                        category_data["quality_issues"].append(
                            f"{filename}: Low quality (file too small)"
                        )

                except pygame.error as e:
                    category_data["quality_issues"].append(f"{filename}: Load error - {e}")

            else:
                category_data["missing_files"].append(filename)

        # Calculate duration statistics
        if durations:
            category_data["duration_stats"] = {
                "min": round(min(durations), 2),
                "max": round(max(durations), 2),
                "mean": round(statistics.mean(durations), 2),
                "median": round(statistics.median(durations), 2),
                "std_dev": round(statistics.stdev(durations) if len(durations) > 1 else 0, 2),
            }

        return category_data

    def _assess_quality(self, duration: float, file_size: int) -> str:
        """Assess the quality of a sound file based on duration and size."""
        # Good educational pronunciation should be 0.7-1.5 seconds
        # and have decent file size for clarity

        duration_good = 0.7 <= duration <= 1.5
        size_good = file_size >= 45000  # At least 45KB for good quality

        if duration_good and size_good:
            return "Excellent"
        elif duration_good or size_good:
            return "Good"
        else:
            return "Needs Improvement"

    def _calculate_overall_metrics(self):
        """Calculate overall quality metrics."""
        all_durations = []
        all_sizes = []
        total_issues = 0

        for category, data in self.results["categories"].items():
            # Collect all durations and sizes
            for filename, details in data["file_details"].items():
                all_durations.append(details["duration"])
                all_sizes.append(details["size_kb"])

            total_issues += len(data["quality_issues"]) + len(data["missing_files"])

        if all_durations:
            self.results["quality_metrics"] = {
                "overall_duration_range": f"{min(all_durations):.2f}s - {max(all_durations):.2f}s",
                "average_duration": f"{statistics.mean(all_durations):.2f}s",
                "duration_consistency": (
                    "Good" if statistics.stdev(all_durations) < 0.3 else "Inconsistent"
                ),
                "average_file_size": f"{statistics.mean(all_sizes):.1f} KB",
                "total_quality_issues": total_issues,
                "overall_quality_score": max(
                    0, 100 - (total_issues * 5)
                ),  # Deduct 5 points per issue
            }

    def _generate_recommendations(self):
        """Generate specific recommendations for improvement."""
        recommendations = []

        # Check for missing files
        missing_count = sum(
            len(data["missing_files"]) for data in self.results["categories"].values()
        )
        if missing_count > 0:
            recommendations.append(f"🚨 CRITICAL: {missing_count} expected audio files are missing")

        # Check duration consistency
        duration_issues = []
        for category, data in self.results["categories"].items():
            if "duration_stats" in data and data["duration_stats"].get("std_dev", 0) > 0.4:
                duration_issues.append(category)

        if duration_issues:
            recommendations.append(f"⚠️ Inconsistent durations in: {', '.join(duration_issues)}")

        # Check for quality issues
        total_quality_issues = sum(
            len(data["quality_issues"]) for data in self.results["categories"].values()
        )
        if total_quality_issues > 0:
            recommendations.append(
                f"🔧 {total_quality_issues} files have quality issues that need attention"
            )

        # Educational recommendations
        if self.results["quality_metrics"].get("overall_quality_score", 0) < 80:
            recommendations.append(
                "📚 Consider regenerating low-quality pronunciation files for better learning experience"
            )

        recommendations.append(
            "✅ Use consistent pronunciation timing (0.7-1.5s) for educational effectiveness"
        )
        recommendations.append("🎯 Ensure clear articulation for all letter/number pronunciations")

        self.results["recommendations"] = recommendations

    def print_detailed_report(self):
        """Print a detailed audit report."""
        print("\n" + "=" * 60)
        print("📊 DETAILED SOUND SYSTEM AUDIT REPORT")
        print("=" * 60)

        print(f"\n🎯 OVERVIEW:")
        print(f"   Total Files Found: {self.results['total_files']}")
        print(
            f"   Overall Quality Score: {self.results['quality_metrics'].get('overall_quality_score', 0)}/100"
        )

        print(f"\n📈 QUALITY METRICS:")
        for key, value in self.results["quality_metrics"].items():
            print(f"   {key.replace('_', ' ').title()}: {value}")

        print(f"\n🗂️ CATEGORY BREAKDOWN:")
        for category, data in self.results["categories"].items():
            print(f"\n   📂 {category.upper()}:")
            print(f"      Files Found: {data['found_count']}/{data['expected_count']}")

            if data["missing_files"]:
                print(f"      ❌ Missing: {', '.join(data['missing_files'])}")

            if "duration_stats" in data:
                stats = data["duration_stats"]
                print(
                    f"      ⏱️ Duration: {stats['min']}s - {stats['max']}s (avg: {stats['mean']}s)"
                )

            if data["quality_issues"]:
                print(f"      ⚠️ Issues: {len(data['quality_issues'])}")
                for issue in data["quality_issues"][:3]:  # Show first 3 issues
                    print(f"         • {issue}")
                if len(data["quality_issues"]) > 3:
                    print(f"         • ... and {len(data['quality_issues']) - 3} more")

        print(f"\n💡 RECOMMENDATIONS:")
        for i, rec in enumerate(self.results["recommendations"], 1):
            print(f"   {i}. {rec}")

        print("\n" + "=" * 60)

    def save_report(self, filename: str = "sound_audit_report.json"):
        """Save the audit report to a JSON file."""
        with open(filename, "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"📄 Detailed report saved to: {filename}")


def main():
    """Main function to run the sound audit."""
    print("🎮 SS6 Sound System Audit Tool")
    print("=" * 40)

    # Create auditor and run analysis
    auditor = SoundAuditor()
    results = auditor.analyze_all_sounds()

    # Print detailed report
    auditor.print_detailed_report()

    # Save report
    auditor.save_report()

    # Quick summary for immediate action
    print(f"\n🚀 QUICK SUMMARY:")
    print(f"   ✅ {results['total_files']} audio files found (expected 48)")
    quality_score = results["quality_metrics"].get("overall_quality_score", 0)
    print(f"   📊 Quality Score: {quality_score}/100")

    if quality_score >= 80:
        print("   🎉 Sound system is in good condition!")
    elif quality_score >= 60:
        print("   ⚠️ Sound system needs some improvements")
    else:
        print("   🚨 Sound system requires significant attention")


if __name__ == "__main__":
    main()
