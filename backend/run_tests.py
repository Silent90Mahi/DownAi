#!/usr/bin/env python
"""
Test Runner Script
Comprehensive test execution utility for the backend
"""
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print('='*60)
    
    result = subprocess.run(cmd, capture_output=False, text=True)
    
    if result.returncode != 0:
        print(f"\n❌ Failed: {description}")
        return False
    
    print(f"\n✅ Success: {description}")
    return True


def main():
    parser = argparse.ArgumentParser(description='Run backend tests')
    parser.add_argument(
        '--type',
        choices=['all', 'unit', 'integration', 'coverage'],
        default='all',
        help='Type of tests to run'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    parser.add_argument(
        '--file',
        type=str,
        help='Run specific test file'
    )
    parser.add_argument(
        '--mark',
        type=str,
        help='Run tests with specific marker (e.g., auth, api)'
    )
    
    args = parser.parse_args()
    
    base_cmd = ['pytest']
    
    if args.verbose:
        base_cmd.append('-v')
    
    success = True
    
    if args.file:
        cmd = base_cmd + [args.file]
        success = run_command(cmd, f"Running tests from {args.file}")
    
    elif args.mark:
        cmd = base_cmd + ['-m', args.mark, 'tests/']
        success = run_command(cmd, f"Running tests marked with @{args.mark}")
    
    elif args.type == 'unit':
        cmd = base_cmd + ['tests/unit/', '-m', 'unit']
        success = run_command(cmd, "Unit Tests")
    
    elif args.type == 'integration':
        cmd = base_cmd + ['tests/integration/', '-m', 'integration']
        success = run_command(cmd, "Integration Tests")
    
    elif args.type == 'coverage':
        cmd = base_cmd + [
            'tests/',
            '--cov=app',
            '--cov-report=html',
            '--cov-report=term',
            '--cov-fail-under=50'
        ]
        success = run_command(cmd, "Tests with Coverage Report")
    
    else:
        print("\n" + "="*60)
        print("RUNNING ALL TESTS")
        print("="*60)
        
        tests = [
            (base_cmd + ['tests/unit/', '-m', 'unit', '-v'], "Unit Tests"),
            (base_cmd + ['tests/integration/', '-m', 'integration', '-v'], "Integration Tests"),
            (base_cmd + ['tests/', '--cov=app', '--cov-report=term-missing'], "Coverage Report"),
        ]
        
        for cmd, description in tests:
            if not run_command(cmd, description):
                success = False
    
    print("\n" + "="*60)
    if success:
        print("✅ ALL TESTS PASSED SUCCESSFULLY!")
    else:
        print("❌ SOME TESTS FAILED")
    print("="*60 + "\n")
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
