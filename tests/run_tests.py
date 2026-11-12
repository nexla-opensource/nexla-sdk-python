#!/usr/bin/env python
"""
Test runner for Nexla SDK tests with organized structure.

Usage:
    # Run all unit tests (default)
    python tests/run_tests.py

    # Run specific test categories
    python tests/run_tests.py --unit
    python tests/run_tests.py --integration
    python tests/run_tests.py --property
    python tests/run_tests.py --models
    python tests/run_tests.py --performance

    # Run specific resources
    python tests/run_tests.py --resource credentials
    python tests/run_tests.py --resource sources

    # Run with various options
    python tests/run_tests.py --coverage
    python tests/run_tests.py --parallel
    python tests/run_tests.py --verbose
    python tests/run_tests.py --slow

    # Run specific test files
    python tests/run_tests.py tests/unit/test_credentials.py
    python tests/run_tests.py tests/integration/test_sources.py

    # Combine options
    python tests/run_tests.py --unit --resource credentials --coverage
    python tests/run_tests.py --integration --parallel --verbose
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import List

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Test categories and their paths
TEST_CATEGORIES = {
    "unit": "tests/unit/",
    "integration": "tests/integration/",
    "property": "tests/property/",
    "models": "tests/models/",
    "performance": "tests/performance/",
}

# Available resources
RESOURCES = [
    "credentials",
    "sources",
    "destinations",
    "nexsets",
    "lookups",
    "users",
    "organizations",
    "teams",
    "projects",
    "notifications",
    "flows",
    "metrics",
    "client",
    "auth",
    "http_client",
]

# Test markers
MARKERS = {
    "unit": "unit",
    "integration": "integration",
    "property": "property",
    "performance": "performance",
    "slow": "slow",
    "requires_setup": "requires_setup",
}


def check_environment():
    """Check if the test environment is properly set up."""
    print("🔍 Checking test environment...")

    # Check for required files
    required_files = [
        "tests/conftest.py",
        "tests/utils/__init__.py",
        "pyproject.toml",
        "requirements.txt",
    ]

    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)

    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        return False

    # Check for test directories
    missing_dirs = []
    for _category, path in TEST_CATEGORIES.items():
        if not Path(path).exists():
            missing_dirs.append(path)

    if missing_dirs:
        print(f"❌ Missing test directories: {missing_dirs}")
        return False

    # Check for dependencies
    try:
        import importlib.util

        required_deps = ["pytest", "hypothesis", "faker"]
        for dep in required_deps:
            if importlib.util.find_spec(dep) is None:
                raise ImportError(f"Missing {dep}")
        print("✅ All required test dependencies are installed")
    except ImportError as e:
        print(f"❌ Missing test dependencies: {e}")
        print("Run: pip install -r requirements.txt")
        return False

    print("✅ Test environment is properly set up")
    return True


def check_credentials():
    """Check if integration test credentials are available."""
    print("🔐 Checking integration test credentials...")

    # Check for .env file
    env_file = Path("tests/.env")
    if not env_file.exists():
        print("⚠️  No .env file found. Integration tests will be skipped.")
        print("Copy tests/env.template to tests/.env and fill in your credentials.")
        return False

    # Check for basic credentials
    from dotenv import load_dotenv

    load_dotenv(env_file)

    service_key = os.getenv("NEXLA_TEST_SERVICE_KEY")
    access_token = os.getenv("NEXLA_TEST_ACCESS_TOKEN")

    if not service_key and not access_token:
        print("⚠️  No authentication credentials found in .env file.")
        print("Set NEXLA_TEST_SERVICE_KEY or NEXLA_TEST_ACCESS_TOKEN")
        return False

    print("✅ Integration test credentials are configured")
    return True


def build_pytest_command(args: argparse.Namespace) -> List[str]:
    """Build the pytest command based on arguments."""
    cmd = ["python", "-m", "pytest"]

    # Add test paths
    test_paths = []

    if args.files:
        # Specific files provided
        test_paths.extend(args.files)
    elif args.category:
        # Specific category
        if args.category in TEST_CATEGORIES:
            test_paths.append(TEST_CATEGORIES[args.category])
        else:
            print(f"❌ Unknown test category: {args.category}")
            sys.exit(1)
    elif args.resource:
        # Specific resource across categories
        for category in args.categories:
            if category in TEST_CATEGORIES:
                resource_file = f"{TEST_CATEGORIES[category]}test_{args.resource}.py"
                if Path(resource_file).exists():
                    test_paths.append(resource_file)
    else:
        # Default to unit tests
        test_paths.append(TEST_CATEGORIES["unit"])

    if test_paths:
        cmd.extend(test_paths)

    # Add markers
    markers = []
    if args.unit:
        markers.append(MARKERS["unit"])
    if args.integration:
        markers.append(MARKERS["integration"])
    if args.property:
        markers.append(MARKERS["property"])
    if args.performance:
        markers.append(MARKERS["performance"])
    if args.slow:
        markers.append(MARKERS["slow"])
    if args.requires_setup:
        markers.append(MARKERS["requires_setup"])

    if markers:
        cmd.extend(["-m", " and ".join(markers)])
    elif not args.files and not args.category:
        # Default to unit tests if no markers specified
        cmd.extend(["-m", MARKERS["unit"]])

    # Add coverage
    if args.coverage:
        cmd.extend(
            [
                "--cov=nexla_sdk",
                "--cov-report=term-missing",
                "--cov-report=html:htmlcov",
                "--cov-report=xml",
                "--cov-fail-under=85",
            ]
        )

    # Add parallel execution
    if args.parallel:
        workers = args.workers or os.cpu_count()
        cmd.extend(["-n", str(workers)])

    # Add verbosity
    if args.verbose:
        cmd.append("-v")
    if args.quiet:
        cmd.append("-q")

    # Add other options
    if args.stop_on_first_failure:
        cmd.append("-x")
    if args.tb_style:
        cmd.extend(["--tb", args.tb_style])
    if args.durations:
        cmd.extend(["--durations", str(args.durations)])

    # Only add hypothesis options if we're running property tests
    if args.property or "property" in str(test_paths):
        if args.hypothesis_examples:
            cmd.extend(["--hypothesis-max-examples", str(args.hypothesis_examples)])

    return cmd


def run_tests(args: argparse.Namespace) -> int:
    """Run the tests with the specified arguments."""
    # Check environment
    if not check_environment():
        return 1

    # Check credentials for integration tests
    if args.integration and not check_credentials():
        print("⚠️  Integration tests require credentials. Skipping.")
        return 0

    # Build pytest command
    cmd = build_pytest_command(args)

    print(f"🚀 Running tests with command: {' '.join(cmd)}")
    print("=" * 80)

    # Run tests
    try:
        result = subprocess.run(cmd, cwd=project_root)
        return result.returncode
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return 1


def show_test_summary():
    """Show a summary of available tests."""
    print("📋 Nexla SDK Test Suite Summary")
    print("=" * 50)

    total_tests = 0
    for category, path in TEST_CATEGORIES.items():
        test_files = list(Path(path).glob("test_*.py"))
        count = len(test_files)
        total_tests += count
        print(f"{category.title():12} tests: {count:2d} files in {path}")

    print(f"{'Total':12} tests: {total_tests:2d} files")
    print()

    print("📦 Available Resources:")
    for i, resource in enumerate(RESOURCES, 1):
        print(f"{i:2d}. {resource}")
    print()

    print("🏷️  Available Markers:")
    for name, marker in MARKERS.items():
        print(f"   {name:15} - {marker}")
    print()


def main():
    """Main entry point for the test runner."""
    parser = argparse.ArgumentParser(
        description="Nexla SDK Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    # Test categories
    test_group = parser.add_argument_group("Test Categories")
    test_group.add_argument("--unit", action="store_true", help="Run unit tests")
    test_group.add_argument(
        "--integration", action="store_true", help="Run integration tests"
    )
    test_group.add_argument(
        "--property", action="store_true", help="Run property-based tests"
    )
    test_group.add_argument(
        "--models", action="store_true", help="Run model validation tests"
    )
    test_group.add_argument(
        "--performance", action="store_true", help="Run performance tests"
    )
    test_group.add_argument(
        "--category", choices=TEST_CATEGORIES.keys(), help="Run specific test category"
    )

    # Resource selection
    resource_group = parser.add_argument_group("Resource Selection")
    resource_group.add_argument(
        "--resource", choices=RESOURCES, help="Run tests for specific resource"
    )
    resource_group.add_argument(
        "--categories",
        nargs="+",
        choices=TEST_CATEGORIES.keys(),
        default=list(TEST_CATEGORIES.keys()),
        help="Categories to search for resource tests",
    )

    # Test markers
    marker_group = parser.add_argument_group("Test Markers")
    marker_group.add_argument("--slow", action="store_true", help="Include slow tests")
    marker_group.add_argument(
        "--requires-setup", action="store_true", help="Include tests requiring setup"
    )

    # Output options
    output_group = parser.add_argument_group("Output Options")
    output_group.add_argument(
        "--coverage", action="store_true", help="Generate coverage report"
    )
    output_group.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output"
    )
    output_group.add_argument("--quiet", "-q", action="store_true", help="Quiet output")
    output_group.add_argument(
        "--tb-style",
        choices=["short", "long", "no"],
        default="short",
        help="Traceback style",
    )

    # Execution options
    exec_group = parser.add_argument_group("Execution Options")
    exec_group.add_argument(
        "--parallel", action="store_true", help="Run tests in parallel"
    )
    exec_group.add_argument("--workers", type=int, help="Number of parallel workers")
    exec_group.add_argument(
        "--stop-on-first-failure",
        "-x",
        action="store_true",
        help="Stop on first failure",
    )
    exec_group.add_argument(
        "--durations", type=int, default=10, help="Show slowest N tests"
    )
    exec_group.add_argument(
        "--hypothesis-examples",
        type=int,
        help="Number of examples for hypothesis tests",
    )

    # Utility options
    util_group = parser.add_argument_group("Utility Options")
    util_group.add_argument(
        "--check-env", action="store_true", help="Check test environment"
    )
    util_group.add_argument(
        "--check-credentials", action="store_true", help="Check integration credentials"
    )
    util_group.add_argument("--summary", action="store_true", help="Show test summary")
    util_group.add_argument(
        "--list-resources", action="store_true", help="List available resources"
    )

    # File arguments
    parser.add_argument("files", nargs="*", help="Specific test files to run")

    args = parser.parse_args()

    # Handle utility options
    if args.check_env:
        return 0 if check_environment() else 1

    if args.check_credentials:
        return 0 if check_credentials() else 1

    if args.summary:
        show_test_summary()
        return 0

    if args.list_resources:
        print("Available resources:")
        for resource in RESOURCES:
            print(f"  - {resource}")
        return 0

    # Run tests
    return run_tests(args)


if __name__ == "__main__":
    sys.exit(main())
