#!/usr/bin/env python3
"""
Sound Performance Test for SS6 Super Student Game
Tests sound loading speed, memory usage, and performance benchmarks.
"""

import pygame
import os
import time
import psutil
import json
from pathlib import Path
from typing import Dict, List, Tuple
import statistics

class SoundPerformanceTester:
    """Tests sound system performance and benchmarks."""
    
    def __init__(self, sounds_dir: str = "sounds"):
        """Initialize the performance tester."""
        self.sounds_dir = Path(sounds_dir)
        
        # Set up headless audio
        os.environ['SDL_AUDIODRIVER'] = 'dummy'
        pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=1024)
        pygame.mixer.init()
        
        self.performance_results = {
            "loading_benchmarks": {},
            "memory_usage": {},
            "timing_analysis": {},
            "performance_score": 0,
            "recommendations": []
        }
        
        # Get baseline memory usage 
        process = psutil.Process()
        self.baseline_memory = process.memory_info().rss / 1024 / 1024  # MB
        
    def benchmark_sound_loading(self) -> Dict:
        """Benchmark sound loading performance."""
        print("⚡ Testing sound loading performance...")
        
        benchmarks = {
            "individual_load_times": {},
            "batch_load_time": 0,
            "cached_access_time": 0,
            "total_sounds_tested": 0
        }
        
        sound_files = list(self.sounds_dir.glob("*.wav"))
        benchmarks["total_sounds_tested"] = len(sound_files)
        
        print(f"   Testing {len(sound_files)} sound files...")
        
        # Test individual loading times
        individual_times = []
        for sound_file in sound_files:
            start_time = time.perf_counter()
            try:
                sound = pygame.mixer.Sound(str(sound_file))
                load_time = time.perf_counter() - start_time
                individual_times.append(load_time)
                benchmarks["individual_load_times"][sound_file.stem] = round(load_time * 1000, 2)  # ms
                if len(benchmarks["individual_load_times"]) <= 5:  # Show first 5
                    print(f"      ✅ {sound_file.stem}: {load_time*1000:.2f}ms")
            except Exception as e:
                benchmarks["individual_load_times"][sound_file.stem] = f"ERROR: {e}"
                print(f"      ❌ {sound_file.stem}: Failed to load")
        
        if len(sound_files) > 5:
            print(f"      ... and {len(sound_files) - 5} more files tested")
        
        # Test batch loading
        print("   Testing batch loading performance...")
        start_time = time.perf_counter()
        sound_cache = {}
        for sound_file in sound_files:
            try:
                sound_cache[sound_file.stem] = pygame.mixer.Sound(str(sound_file))
            except:
                pass
        batch_time = time.perf_counter() - start_time
        benchmarks["batch_load_time"] = round(batch_time * 1000, 2)
        print(f"      Batch load time: {batch_time*1000:.2f}ms")
        
        # Test cached access
        if sound_cache:
            print("   Testing cached access performance...")
            start_time = time.perf_counter()
            for _ in range(100):  # Access each sound 100 times
                for sound_name, sound in sound_cache.items():
                    _ = sound.get_length()  # Fast access operation
            cached_time = time.perf_counter() - start_time
            benchmarks["cached_access_time"] = round(cached_time * 1000, 2)
            print(f"      Cached access (100 iterations): {cached_time*1000:.2f}ms")
        
        # Calculate statistics
        if individual_times:
            benchmarks["loading_stats"] = {
                "min_load_time_ms": round(min(individual_times) * 1000, 2),
                "max_load_time_ms": round(max(individual_times) * 1000, 2),
                "avg_load_time_ms": round(statistics.mean(individual_times) * 1000, 2),
                "total_load_time_ms": round(sum(individual_times) * 1000, 2)
            }
        
        return benchmarks
    
    def analyze_memory_usage(self) -> Dict:
        """Analyze memory usage with sounds loaded."""
        print("🧠 Analyzing memory usage...")
        
        memory_analysis = {
            "baseline_mb": round(self.baseline_memory, 2),
            "with_sounds_mb": 0,
            "memory_per_sound_kb": 0,
            "memory_efficiency": "unknown"
        }
        
        # Load all sounds and measure memory
        sound_cache = {}
        sound_files = list(self.sounds_dir.glob("*.wav"))
        
        for sound_file in sound_files:
            try:
                sound_cache[sound_file.stem] = pygame.mixer.Sound(str(sound_file))
            except:
                pass
        
        # Measure memory with sounds loaded
        process = psutil.Process()
        memory_with_sounds = process.memory_info().rss / 1024 / 1024  # MB
        memory_analysis["with_sounds_mb"] = round(memory_with_sounds, 2)
        
        # Calculate memory per sound
        memory_increase = memory_with_sounds - self.baseline_memory
        if len(sound_cache) > 0:
            memory_per_sound = (memory_increase * 1024) / len(sound_cache)  # KB per sound
            memory_analysis["memory_per_sound_kb"] = round(memory_per_sound, 2)
        
        # Assess efficiency
        if memory_increase < 50:  # Less than 50MB increase
            memory_analysis["memory_efficiency"] = "Excellent"
        elif memory_increase < 100:  # Less than 100MB increase
            memory_analysis["memory_efficiency"] = "Good"
        else:
            memory_analysis["memory_efficiency"] = "Needs Optimization"
        
        print(f"   Baseline memory: {memory_analysis['baseline_mb']} MB")
        print(f"   With sounds loaded: {memory_analysis['with_sounds_mb']} MB")
        print(f"   Memory increase: {round(memory_increase, 2)} MB")
        print(f"   Memory per sound: {memory_analysis['memory_per_sound_kb']} KB")
        print(f"   Efficiency rating: {memory_analysis['memory_efficiency']}")
        
        return memory_analysis
    
    def analyze_sound_timing(self) -> Dict:
        """Analyze sound timing and educational effectiveness."""
        print("⏱️ Analyzing sound timing for educational effectiveness...")
        
        timing_analysis = {
            "pronunciation_timing": {},
            "effect_timing": {},
            "educational_effectiveness": {},
            "timing_consistency": "unknown"
        }
        
        sound_files = list(self.sounds_dir.glob("*.wav"))
        
        # Categorize sounds for timing analysis
        categories = {
            "letters": [],
            "numbers": [],
            "colors": [],
            "shapes": [],
            "effects": []
        }
        
        for sound_file in sound_files:
            name = sound_file.stem
            try:
                sound = pygame.mixer.Sound(str(sound_file))
                duration = sound.get_length()
                
                # Categorize the sound
                if name.isalpha() and len(name) == 1:
                    categories["letters"].append((name, duration))
                elif name.isdigit():
                    categories["numbers"].append((name, duration))
                elif name in ["red", "blue", "green", "yellow", "purple"]:
                    categories["colors"].append((name, duration))
                elif name in ["circle", "square", "triangle", "rectangle", "pentagon"]:
                    categories["shapes"].append((name, duration))
                elif name in ["explosion", "laser"]:
                    categories["effects"].append((name, duration))
                    
            except Exception as e:
                print(f"      ❌ Failed to analyze {name}: {e}")
        
        # Analyze each category
        for category, sounds in categories.items():
            if sounds:
                durations = [duration for _, duration in sounds]
                timing_analysis["pronunciation_timing"][category] = {
                    "count": len(sounds),
                    "min_duration": round(min(durations), 2),
                    "max_duration": round(max(durations), 2),
                    "avg_duration": round(statistics.mean(durations), 2),
                    "std_dev": round(statistics.stdev(durations) if len(durations) > 1 else 0, 2),
                    "educational_rating": self._rate_educational_timing(durations, category)
                }
                
                print(f"   📂 {category.upper()}: {len(sounds)} sounds, "
                      f"avg {round(statistics.mean(durations), 2)}s, "
                      f"rating: {timing_analysis['pronunciation_timing'][category]['educational_rating']}")
        
        # Overall timing consistency
        all_durations = []
        for category_data in timing_analysis["pronunciation_timing"].values():
            if "avg_duration" in category_data:
                all_durations.append(category_data["avg_duration"])
        
        if all_durations and len(all_durations) > 1:
            overall_std = statistics.stdev(all_durations)
            if overall_std < 0.2:
                timing_analysis["timing_consistency"] = "Excellent"
            elif overall_std < 0.4:
                timing_analysis["timing_consistency"] = "Good"
            else:
                timing_analysis["timing_consistency"] = "Inconsistent"
        
        return timing_analysis
    
    def _rate_educational_timing(self, durations: List[float], category: str) -> str:
        """Rate the educational effectiveness of timing."""
        avg_duration = statistics.mean(durations)
        std_dev = statistics.stdev(durations) if len(durations) > 1 else 0
        
        # Ideal timing for different categories
        if category in ["letters", "numbers"]:
            # Short, clear pronunciation: 0.7-1.3s
            if 0.7 <= avg_duration <= 1.3 and std_dev < 0.3:
                return "Excellent"
            elif 0.5 <= avg_duration <= 1.6:
                return "Good"
            else:
                return "Needs Improvement"
        elif category in ["colors", "shapes"]:
            # Slightly longer for complex words: 1.0-1.8s
            if 1.0 <= avg_duration <= 1.8 and std_dev < 0.3:
                return "Excellent"
            elif 0.8 <= avg_duration <= 2.0:
                return "Good"
            else:
                return "Needs Improvement"
        elif category == "effects":
            # Quick sound effects: 0.2-0.8s
            if 0.2 <= avg_duration <= 0.8:
                return "Excellent"
            else:
                return "Good"
        
        return "Unknown"
    
    def calculate_performance_score(self) -> int:
        """Calculate overall performance score."""
        score = 100  # Start with perfect score
        
        # Deduct points for loading performance issues
        loading_stats = self.performance_results["loading_benchmarks"].get("loading_stats", {})
        avg_load = loading_stats.get("avg_load_time_ms", 0)
        if avg_load > 100:  # More than 100ms per sound
            score -= 20
        elif avg_load > 50:  # More than 50ms per sound
            score -= 10
        
        # Deduct points for memory issues
        memory_efficiency = self.performance_results["memory_usage"].get("memory_efficiency", "Good")
        if memory_efficiency == "Needs Optimization":
            score -= 25
        elif memory_efficiency == "Good":
            score -= 5
        
        # Deduct points for timing issues
        timing_consistency = self.performance_results["timing_analysis"].get("timing_consistency", "Good")
        if timing_consistency == "Inconsistent":
            score -= 20
        elif timing_consistency == "Good":
            score -= 5
        
        return max(0, score)
    
    def generate_recommendations(self):
        """Generate performance recommendations."""
        recommendations = []
        
        # Loading performance recommendations
        loading_stats = self.performance_results["loading_benchmarks"].get("loading_stats", {})
        avg_load = loading_stats.get("avg_load_time_ms", 0)
        if avg_load > 50:
            recommendations.append(f"⚡ Loading performance: Average {avg_load:.1f}ms per sound - consider audio compression")
        
        # Memory recommendations
        memory_mb = self.performance_results["memory_usage"].get("memory_per_sound_kb", 0)
        if memory_mb > 100:  # More than 100KB per sound
            recommendations.append(f"🧠 Memory usage: {memory_mb:.1f}KB per sound - consider optimizing audio quality vs size")
        
        # Timing recommendations
        timing_data = self.performance_results["timing_analysis"].get("pronunciation_timing", {})
        for category, data in timing_data.items():
            if data.get("educational_rating") == "Needs Improvement":
                recommendations.append(f"🎯 {category.title()} timing needs improvement - avg {data['avg_duration']}s")
        
        # General recommendations
        recommendations.append("✅ Pre-cache frequently used sounds for better performance")
        recommendations.append("🎵 Use consistent audio format (44.1kHz, 16-bit) for all sounds")
        recommendations.append("📚 Keep pronunciation timing between 0.7-1.5s for optimal learning")
        
        self.performance_results["recommendations"] = recommendations
    
    def run_comprehensive_test(self) -> Dict:
        """Run comprehensive performance test."""
        print("🚀 SS6 Sound Performance Test")
        print("=" * 50)
        
        # Run all performance tests
        self.performance_results["loading_benchmarks"] = self.benchmark_sound_loading()
        print()
        
        self.performance_results["memory_usage"] = self.analyze_memory_usage()
        print()
        
        self.performance_results["timing_analysis"] = self.analyze_sound_timing()
        print()
        
        # Calculate overall score and recommendations
        self.performance_results["performance_score"] = self.calculate_performance_score()
        self.generate_recommendations()
        
        return self.performance_results
    
    def print_performance_report(self):
        """Print comprehensive performance report."""
        print("\n" + "=" * 50)
        print("📊 SOUND PERFORMANCE REPORT")
        print("=" * 50)
        
        score = self.performance_results["performance_score"]
        print(f"\n🎯 OVERALL PERFORMANCE SCORE: {score}/100")
        
        if score >= 90:
            print("   🎉 Excellent performance!")
        elif score >= 75:
            print("   ✅ Good performance")
        elif score >= 60:
            print("   ⚠️ Acceptable performance with room for improvement")
        else:
            print("   🚨 Performance needs attention") 
        
        # Loading performance
        loading_stats = self.performance_results["loading_benchmarks"].get("loading_stats", {})
        if loading_stats:
            print(f"\n⚡ LOADING PERFORMANCE:")
            print(f"   Average load time: {loading_stats.get('avg_load_time_ms', 0):.1f}ms per sound")
            print(f"   Total load time: {loading_stats.get('total_load_time_ms', 0):.1f}ms for all sounds")
        
        # Memory usage
        memory = self.performance_results["memory_usage"]
        print(f"\n🧠 MEMORY USAGE:")
        print(f"   Memory per sound: {memory.get('memory_per_sound_kb', 0):.1f} KB")
        print(f"   Total memory increase: {memory.get('with_sounds_mb', 0) - memory.get('baseline_mb', 0):.1f} MB")
        print(f"   Efficiency: {memory.get('memory_efficiency', 'Unknown')}")
        
        # Timing analysis
        timing = self.performance_results["timing_analysis"].get("pronunciation_timing", {})
        if timing:
            print(f"\n⏱️ TIMING ANALYSIS:")
            for category, data in timing.items():
                print(f"   {category.title()}: {data['avg_duration']:.2f}s avg, {data['educational_rating']} rating")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        for i, rec in enumerate(self.performance_results["recommendations"], 1):
            print(f"   {i}. {rec}")
        
        print("\n" + "=" * 50)
    
    def save_performance_report(self, filename: str = "sound_performance_report.json"):
        """Save performance report to file."""
        with open(filename, 'w') as f:
            json.dump(self.performance_results, f, indent=2)
        print(f"📄 Performance report saved to: {filename}")

def main():
    """Main function to run sound performance tests."""
    tester = SoundPerformanceTester()
    
    # Run comprehensive performance test
    results = tester.run_comprehensive_test()
    
    # Print performance report
    tester.print_performance_report()
    
    # Save detailed report
    tester.save_performance_report()

if __name__ == "__main__":
    main()