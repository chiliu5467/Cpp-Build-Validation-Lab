import sys
import unittest
import subprocess
import json
import tempfile

from pathlib import Path
from unittest.mock import patch

TOOLS_DIR = Path(__file__).resolve().parents[1] / "tools"

sys.path.insert(0, str(TOOLS_DIR))

import validate

def make_step(name, success):
    return {
        "name": name,
        "success": success,
        "returncode": 0 if success else 1,
        "duration_seconds": 0.1,
        "stdout": "",
        "stderr": ""
    }


class TestBuildValidation(unittest.TestCase):

    def test_run_command_success(self):
        command = ["cmake", "--version"]

        fake_result = subprocess.CompletedProcess(
            args=command,
            returncode=0,
            stdout="CMake OK",
            stderr=""
        )

        with patch(
            "validate.subprocess.run",
            return_value=fake_result
        ) as mock_run:

            result = validate.run_command(
                "CMake Version",
                command
            )

        self.assertTrue(result["success"])
        self.assertEqual(result["returncode"], 0)
        self.assertEqual(result["name"], "CMake Version")
        self.assertEqual(result["stdout"], "CMake OK")
        mock_run.assert_called_once()


    def test_run_command_failure(self):
        command = ["ctest", "--version"]
        
        fake_result = subprocess.CompletedProcess(
            args=command,
            returncode=8,
            stdout="CTest failed",
            stderr="Test execution failed"
        )

        with patch(
            "validate.subprocess.run",
            return_value=fake_result
        ) as mock_run:

            result = validate.run_command(
                "CTest Version",
                command
            )

        self.assertFalse(result["success"])
        self.assertEqual(result["returncode"], 8)
        self.assertEqual(result["name"], "CTest Version")
        self.assertEqual(result["stdout"], "CTest failed")
        self.assertEqual(result["stderr"], "Test execution failed")
        mock_run.assert_called_once()

    def test_build_failure_stops_testing(self):
        with (
            patch.object(
                sys,
                "argv",
                ["validate.py", "--config", "Debug"]
            ),
            patch(
                "validate.configure_project",
                return_value=make_step("Configure", True)
            ),
            patch(
                "validate.build_project",
                return_value=make_step("Build", False)
            ),
            patch("validate.test_project") as mock_test,
            patch("validate.save_report") as mock_save
        ):
            exit_code = validate.main()

            self.assertEqual(exit_code, 1)
            mock_test.assert_not_called()
            mock_save.assert_called_once()
            configuration, steps = mock_save.call_args.args

            self.assertEqual(configuration, "Debug")
            self.assertEqual(
                [step["name"] for step in steps],
                ["Configure", "Build"]
            )

    def test_testing_failure(self):
        with (
            patch.object(
                sys,
                "argv",
                ["validate.py", "--config", "Debug"]
            ),
            patch(
                "validate.configure_project",
                return_value=make_step("Configure", True)
            ),
            patch(
                "validate.build_project",
                return_value=make_step("Build", True)
            )as mock_build,
            patch(
                "validate.test_project",
                return_value=make_step("Test", False)
            ) as mock_test,
            patch("validate.save_report") as mock_save
        ):
            exit_code = validate.main()

            self.assertEqual(exit_code, 1)
            mock_build.assert_called_once()
            mock_test.assert_called_once()
            mock_save.assert_called_once()

            configuration, steps = mock_save.call_args.args

            self.assertEqual(configuration, "Debug")
            self.assertEqual(
                [step["name"] for step in steps],
                ["Configure", "Build", "Test"]
            )
            self.assertFalse(steps[2]["success"])

    def test_all_pass(self):
        with (
            patch.object(
                sys,
                "argv",
                ["validate.py", "--config", "Debug"]
            ),
            patch(
                "validate.configure_project",
                return_value=make_step("Configure", True)
            ),
            patch(
                "validate.build_project",
                return_value=make_step("Build", True)
            )as mock_build,
            patch(
                "validate.test_project",
                return_value=make_step("Test", True)
            ) as mock_test,
            patch("validate.save_report") as mock_save
        ):
            exit_code = validate.main()

            self.assertEqual(exit_code, 0)
            mock_build.assert_called_once()
            mock_test.assert_called_once()
            mock_save.assert_called_once()

            configuration, steps = mock_save.call_args.args

            self.assertEqual(configuration, "Debug")
            self.assertEqual(
                [step["name"] for step in steps],
                ["Configure", "Build", "Test"]
            )
            self.assertTrue(steps[0]["success"])
            self.assertTrue(steps[1]["success"])
            self.assertTrue(steps[2]["success"])

    def test_configure_failure(self):
        with (
            patch.object(
                sys,
                "argv",
                ["validate.py", "--config", "Debug"]
            ),
            patch(
                "validate.configure_project",
                return_value=make_step("Configure", False)
            ) as mock_configure,
            patch("validate.build_project") as mock_build,
            patch("validate.test_project") as mock_test,
            patch("validate.save_report") as mock_save
        ):
            exit_code = validate.main()

            self.assertEqual(exit_code, 1)
            mock_configure.assert_called_once()
            mock_build.assert_not_called()
            mock_test.assert_not_called()
            mock_save.assert_called_once()

            configuration, steps = mock_save.call_args.args

            self.assertEqual(configuration, "Debug")
            self.assertEqual(
                [step["name"] for step in steps],
                ["Configure"]
            )
            self.assertFalse(steps[0]["success"])

    def test_save_report_json(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temporary_root = Path(temp_dir)

            with patch.object(
                validate,
                "PROJECT_ROOT",
                temporary_root
            ):
                validate.save_report(
                    "Debug",
                    [
                        make_step("Configure", True),
                        make_step("Build", True),
                        make_step("Test", True)
                    ]
                )

            report_path = (
                temporary_root
                / "reports"
                / "validation-Debug.json"
            )

            self.assertTrue(report_path.is_file())

            with report_path.open("r", encoding="utf-8") as file:
                report = json.load(file)

            self.assertEqual(report["configuration"], "Debug")
            self.assertTrue(report["success"])
            self.assertEqual(len(report["steps"]), 3)
            self.assertEqual(
                [step["name"] for step in report["steps"]],
                ["Configure", "Build", "Test"]
            )

if __name__ == "__main__":
    unittest.main()