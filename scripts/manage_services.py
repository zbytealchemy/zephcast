#!/usr/bin/env python3
"""Script to manage Docker services for development and testing."""

import argparse
import subprocess
import sys
import time

from typing import List, Optional


def run_command(command: List[str], check: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command."""
    return subprocess.run(command, check=check, capture_output=True, text=True)


def docker_compose_cmd(command: List[str], check: bool = True) -> subprocess.CompletedProcess:
    """Run a docker-compose command."""
    return run_command(["docker", "compose"], *command, check=check)


def wait_for_services() -> None:
    """Wait for all services to be healthy."""
    print("Waiting for services to be healthy...")
    max_attempts = 30
    attempt = 0

    while attempt < max_attempts:
        try:
            result = docker_compose_cmd(["ps", "--format", "json"], check=False)
            if "healthy" in result.stdout and "unhealthy" not in result.stdout:
                print("All services are healthy!")
                return
        except subprocess.CalledProcessError:
            pass

        time.sleep(2)
        attempt += 1
        if attempt % 5 == 0:
            print(f"Still waiting... ({attempt}/{max_attempts})")

    print("Error: Services did not become healthy in time", file=sys.stderr)
    sys.exit(1)


def start_services(services: Optional[List[str]] = None) -> None:
    """Start Docker services."""
    cmd = ["up", "-d"]
    if services:
        cmd.extend(services)

    print("Starting services...")
    docker_compose_cmd(cmd)
    wait_for_services()


def stop_services() -> None:
    """Stop Docker services."""
    print("Stopping services...")
    docker_compose_cmd(["down"])


def check_services() -> None:
    """Check service status."""
    print("Checking service status...")
    docker_compose_cmd(["ps"])


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Manage Docker services for development and testing"
    )
    parser.add_argument("action", choices=["start", "stop", "status"], help="Action to perform")
    parser.add_argument("--services", nargs="+", help="Specific services to start")

    args = parser.parse_args()

    try:
        if args.action == "start":
            start_services(args.services)
        elif args.action == "stop":
            stop_services()
        elif args.action == "status":
            check_services()
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
