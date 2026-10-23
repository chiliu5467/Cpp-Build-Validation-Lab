# C++ Build Validation Lab

A Python-based build validation tool that automates the configuration, compilation, and testing of a C++20 project using CMake and CTest.

## Overview

This project demonstrates how Python can be used to automate a C++ development workflow, handle build failures, and generate structured validation reports.

The validation pipeline consists of three stages:

1. **Configure** — Generate build files using CMake.
2. **Build** — Compile the C++ project.
3. **Test** — Execute registered tests using CTest.

If any stage fails, the pipeline stops immediately and generates a JSON validation report.

## Features

- Automated CMake configuration, build, and CTest execution
- Support for Debug and Release configurations
- Fail-fast execution on configuration, build, or test failure
- Structured JSON reports with execution status, duration, and exit codes
- Logging with detailed error messages
- Handling of external process launch failures (`FileNotFoundError`, `PermissionError`)
- Python unit tests using `unittest` and `unittest.mock`
- C++20 checksum library for integration testing

## Tech Stack

| Technology | Purpose |
|------------|---------|
| C++20 | Test library implementation |
| Python 3 | Build automation |
| CMake | Build configuration and compilation |
| CTest | C++ test execution |
| unittest | Python unit testing |
| unittest.mock | Mock external process execution |
| JSON | Structured validation reports |

## Project Structure

```text
Cpp-Build-Validation-Lab/
├── CMakeLists.txt
├── CMakePresets.json
├── .gitignore
├── README.md
│
└── Cpp-Build-Validation-Lab/
    ├── include/
    │   └── Checksum.h
    │
    ├── src/
    │   └── Checksum.cpp
    │
    ├── tests/
    │   ├── test_checksum.cpp
    │   └── test_validate.py
    │
    └── tools/
        └── validate.py
```

## Requirements

- Python 3
- CMake 3.20 or newer
- C++20-compatible compiler
- CTest (included with CMake)

Ensure Python, CMake, and a C++ compiler are available in your development environment.

## Getting Started

Clone the repository:

```bash
git clone https://github.com/chiliu5467/Cpp-Build-Validation-Lab.git

cd Cpp-Build-Validation-Lab
```

All commands below assume you are in the repository root directory containing `CMakeLists.txt`.

### Debug Validation

```bash
python Cpp-Build-Validation-Lab/tools/validate.py --config Debug
```

### Release Validation

```bash
python Cpp-Build-Validation-Lab/tools/validate.py --config Release
```

The script automatically executes:

```text
Configure
    |
    v
Build
    |
    v
CTest
    |
    v
Generate JSON Report
```

If any step fails, subsequent stages are skipped.

## Running Tests

### Python Unit Tests

Run the Python test suite:

```bash
python -m unittest discover -s Cpp-Build-Validation-Lab/tests -p "test_validate.py" -v
```

The tests use `unittest.mock` to simulate external commands without running CMake or the C++ compiler.

Test scenarios include:

- Successful command execution
- Failed command execution
- Configure failure
- Build failure
- Test failure
- Successful validation pipeline
- JSON report generation
- Missing external executable (`FileNotFoundError`)
- Permission errors (`PermissionError`)
- CTest command validation

### C++ Integration Tests

The project includes a simple C++20 checksum library.

The checksum function calculates the sum of byte values:

```cpp
std::uint32_t ComputeChecksum(
    std::span<const std::byte> bytes);
```

Example:

```text
Input:  01 02 03
Output: 6
```

The C++ test executable checks normal and edge cases.

After building the Debug configuration, run:

```bash
ctest --test-dir out/build/debug -C Debug --output-on-failure --no-tests=error
```

For Release:

```bash
ctest --test-dir out/build/release -C Release --output-on-failure --no-tests=error
```

## JSON Validation Reports

After validation, the tool generates:

```text
reports/
├── validation-Debug.json
└── validation-Release.json
```

### Example Report

The following is an abbreviated example:

```json
{
  "project": "Cpp-Build-Validation-Lab",
  "configuration": "Debug",
  "success": true,
  "total_duration_seconds": 2.5,
  "steps": [
    {
      "name": "Configure",
      "success": true,
      "returncode": 0,
      "duration_seconds": 0.5
    },
    {
      "name": "Build",
      "success": true,
      "returncode": 0,
      "duration_seconds": 1.8
    },
    {
      "name": "Test",
      "success": true,
      "returncode": 0,
      "duration_seconds": 0.2
    }
  ]
}
```

Actual reports also include the executed command, `stdout`, and `stderr`.

Each validation step records:

| Field | Description |
|-------|-------------|
| name | Validation stage |
| command | Executed command |
| success | Whether the command succeeded |
| returncode | External process exit code |
| duration_seconds | Execution duration |
| stdout | Standard output |
| stderr | Standard error |

If an external process cannot start, `returncode` is recorded as `null`, and the report includes an `error_type`.

## Error Handling

The validation tool distinguishes between two failure scenarios.

### 1. Process Execution Failure

The external process starts but returns a nonzero exit code.

```text
CMake starts
    |
    v
Build fails
    |
    v
returncode != 0
    |
    v
Stop pipeline
```

### 2. Process Launch Failure

The external executable cannot start.

Examples:

- `FileNotFoundError`
- `PermissionError`

```text
External command
    |
    v
OSError
    |
    v
Structured Failure Result
    |
    v
Save JSON Report
    |
    v
Stop pipeline
```

In this case, `returncode` is set to `None` in Python and serialized as `null` in JSON because the process did not return an exit code.

## Testing Strategy

The project combines two testing approaches.

### Unit Testing

Python unit tests use Mock objects to simulate external command execution.

This allows the validation tool's control flow to be tested without requiring a real C++ build.

### Integration Testing

Integration tests execute the actual CMake, compiler, and CTest commands.

This verifies that the complete build pipeline works correctly.

Both approaches are necessary because mocked tests cannot guarantee that the real compiler, build system, and test environment will work correctly.

## Design Decisions

### Fail-Fast Validation

The pipeline stops immediately when a validation stage fails.

This prevents invalid or outdated build artifacts from being treated as successful results.

### Structured Results

Each command returns a structured dictionary containing execution status and diagnostic information.

This makes the validation results easier to inspect, store, and process.

### Test Isolation

Python unit tests use Mock objects and temporary directories to avoid modifying real build artifacts or validation reports.

### Debug and Release Support

The tool supports separate Debug and Release build directories.

Both configurations can be validated independently.

## What I Learned

Through this project, I practiced:

- Automating C++ build and testing workflows using Python
- Managing external processes with `subprocess.run()`
- Designing fail-fast validation pipelines
- Handling process execution and launch failures
- Creating structured JSON reports
- Measuring execution duration
- Writing Python unit tests with `unittest`
- Using Mock objects to test external dependencies
- Understanding the differences between unit and integration testing
- Validating C++ projects in Debug and Release configurations

## Future Improvements

Potential improvements include:

- GitHub Actions CI integration
- Automated validation across multiple operating systems
- Configurable compiler and CMake generator selection
- More detailed CTest result summaries
- Additional report formats
- Automated build artifact packaging
