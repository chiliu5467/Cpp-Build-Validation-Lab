import subprocess
from pathlib import Path
import argparse

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def run_command(command):
    print(f"Running: {' '.join(command)}", flush=True)

    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        check=False
    )

    return result.returncode == 0

if __name__ == "__main__":
    success = run_command(["cmake", "--version"])
    print("Success:", success)

def configure_project(config):
    build_dir = "out/build/" + config.lower()
    command = [
            "cmake",
            "-S",
            ".",
            "-B",
            build_dir,
            "-DCMAKE_BUILD_TYPE=" + config
        ]
    return run_command(command)

if __name__ == "__main__":
    success = configure_project("Debug")
    print("Configure Success:", success)

def build_project(config):
    build_dir = "out/build/" + config.lower()

    command = [
        "cmake",
        "--build",
        build_dir,
        "--config",
        config
    ]

    return run_command(command)

if __name__ == "__main__":
    configure_success = configure_project("Debug")
    print("Configure Success:", configure_success)

    if configure_success:
        build_success = build_project("Debug")
        print("Build Success:", build_success)

def test_project(config):
    build_dir = "out/build/" + config.lower()

    command = [
        "ctest",
        "--test-dir",
        build_dir,
        "-C",
        config,
        "--output-on-failure"
    ]

    return run_command(command)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--config",
        choices=["Debug", "Release"],
        default="Debug"
    )

    args = parser.parse_args()

    config = args.config

    if not configure_project(config):
        raise SystemExit(1)

    if not build_project(config):
        raise SystemExit(1)

    if not test_project(config):
        raise SystemExit(1)

    print("All validation steps passed!")


parser = argparse.ArgumentParser()

parser.add_argument(
    "--config",
    choices=["Debug", "Release"],
    default="Debug"
)

args = parser.parse_args()