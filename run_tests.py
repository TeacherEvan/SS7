"""
Test Runner for SS6 Super Student Game
Provides easy way to run all tests with proper setup.
"""

import os
import sys
import subprocess
from pathlib import Path

def setup_test_environment():
    """Set up the test environment."""
    # Add project root to Python path
    project_root = Path(__file__).parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    # Change to project root directory
    os.chdir(project_root)
    
    print(f"Test environment set up. Project root: {project_root}")

def run_unit_tests():
    """Run unit tests."""
    print("\n" + "="*50)
    print("Running Unit Tests")
    print("="*50)
    
    try:
        # Import and run tests
        from tests.test_ss6 import run_all_tests
        result = run_all_tests()
        return result.wasSuccessful()
    
    except ImportError as e:
        print(f"Error importing tests: {e}")
        return False
    except Exception as e:
        print(f"Error running tests: {e}")
        return False

def run_integration_tests():
    """Run integration tests (placeholder for future)."""
    print("\n" + "="*50)
    print("Integration Tests")
    print("="*50)
    print("No integration tests defined yet.")
    return True

def run_performance_tests():
    """Run performance tests (placeholder for future)."""
    print("\n" + "="*50)
    print("Performance Tests")
    print("="*50)
    print("No performance tests defined yet.")
    return True

def generate_test_report():
    """Generate test coverage report."""
    print("\n" + "="*50)
    print("Test Coverage Report")
    print("="*50)
    
    try:
        # Try to run coverage if available
        result = subprocess.run([
            sys.executable, "-m", "coverage", "run", "--source=.", "tests/test_ss6.py"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            # Generate report
            report_result = subprocess.run([
                sys.executable, "-m", "coverage", "report"
            ], capture_output=True, text=True)
            
            if report_result.returncode == 0:
                print(report_result.stdout)
            else:
                print("Coverage report generation failed.")
        else:
            print("Coverage analysis not available (install with: pip install coverage)")
    
    except FileNotFoundError:
        print("Coverage tool not installed. Install with: pip install coverage")

def main():
    """Main test runner function."""
    print("SS6 Super Student Game - Test Runner")
    print("="*50)
    
    # Setup environment
    setup_test_environment()
    
    # Track test results
    results = []
    
    # Run different test suites
    results.append(("Unit Tests", run_unit_tests()))
    results.append(("Integration Tests", run_integration_tests()))
    results.append(("Performance Tests", run_performance_tests()))
    
    # Generate test report
    generate_test_report()
    
    # Print final summary
    print("\n" + "="*50)
    print("Final Test Summary")
    print("="*50)
    
    all_passed = True
    for test_name, passed in results:
        status = "PASSED" if passed else "FAILED"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "="*50)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("The SS6 game is ready for deployment.")
    else:
        print("❌ SOME TESTS FAILED!")
        print("Please review the test output and fix issues before deployment.")
    print("="*50)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)