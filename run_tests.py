#!/usr/bin/env python3
"""
Test runner for InternGenius application
Run all tests with: python run_tests.py
"""

import unittest
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_tests():
    """Discover and run all tests"""
    # Create test loader
    loader = unittest.TestLoader()
    
    # Discover tests in the tests directory
    start_dir = os.path.join(os.path.dirname(__file__), 'tests')
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Create test runner with verbosity
    runner = unittest.TextTestRunner(verbosity=2)
    
    # Run tests
    result = runner.run(suite)
    
    # Return exit code based on test results
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    exit_code = run_tests()
    sys.exit(exit_code)
