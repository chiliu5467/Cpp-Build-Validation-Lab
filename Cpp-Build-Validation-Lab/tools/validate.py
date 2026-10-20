import argparse
import subprocess
from pathlib import Path
import logging
import json
import time

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s | %(message)s"
)

def run_command(name, command):
    logging.info("Starting %s", name)
    start = time.perf_counter()

    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False
    )

    duration = time.perf_counter() - start

    if result.returncode == 0:
        logging.info(
            "%s completed in %.3f seconds",
            name,
            duration
        )
    else:
        logging.error(
            "%s failed with exit code %d",
            name,
            result.returncode
        )

        if result.stdout:
            logging.error("stdout:\n%s", result.stdout)

        if result.stderr:
            logging.error("stderr:\n%s", result.stderr)

    return {
        "name": name,
        "command": command,
        "success": result.returncode == 0,
        "returncode": result.returncode,
        "duration_seconds": round(duration, 3),
        "stdout": result.stdout,
        "stderr": result.stderr
    }

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
    return run_command("Configure", command)

def build_project(config):
    build_dir = "out/build/" + config.lower()

    command = [
        "cmake",
        "--build",
        build_dir,
        "--config",
        config
    ]

    return run_command("Build", command)

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

    return run_command("Test Project", command)

def save_report(config, steps):
    reports_dir = PROJECT_ROOT / "reports"

    reports_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    report = {
        "project": "Cpp-Build-Validation-Lab",
        "configuration": config,
        "success": len(steps) == 3 and all(
            step["success"] for step in steps
        ),
        "total_duration_seconds": round(
            sum(step["duration_seconds"] for step in steps), 3
        ),
        "steps": steps
    }

    report_path = reports_dir / f"validation-{config}.json"

    with report_path.open("w", encoding="utf-8") as f:
        json.dump(
            report,
            f,
            indent=2,
            ensure_ascii=False
        )

    logging.info("Report saved to %s", report_path)

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--config",
        choices=["Debug", "Release"],
        default="Debug"
    )

    args = parser.parse_args()
    config = args.config

    steps = []

    # Configure
    configure_result = configure_project(config)
    steps.append(configure_result)

    if not configure_result["success"]:
        save_report(config, steps)
        return 1

    # Build
    build_result = build_project(config)
    steps.append(build_result)

    if not build_result["success"]:
        save_report(config, steps)
        return 1

    # Test
    test_result = test_project(config)
    steps.append(test_result)

    if not test_result["success"]:
        save_report(config, steps)
        return 1

    # All steps passed
    save_report(config, steps)
    
    logging.info("All validation steps passed!")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

