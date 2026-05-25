import pathlib
import sys
import threading
import unittest

import flet as ft

PROJECT_ROOT = pathlib.Path(__file__).parent.parent.parent.parent


def _ensure_project_in_path() -> None:
    root_str = str(PROJECT_ROOT)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)


class _CollectingResult(unittest.TestResult):

    def __init__(self):
        super().__init__()
        self.collected: list[dict] = []

    def addSuccess(self, test):
        super().addSuccess(test)
        self.collected.append({
            "class": type(test).__name__,
            "name": test._testMethodName,
            "status": "pass",
            "message": None,
        })

    def addFailure(self, test, err):
        super().addFailure(test, err)
        lines = self._exc_info_to_string(err, test).strip().splitlines()
        self.collected.append({
            "class": type(test).__name__,
            "name": test._testMethodName,
            "status": "fail",
            "message": lines[-1] if lines else "Assertion failed",
        })

    def addError(self, test, err):
        super().addError(test, err)
        lines = self._exc_info_to_string(err, test).strip().splitlines()
        self.collected.append({
            "class": type(test).__name__,
            "name": test._testMethodName,
            "status": "error",
            "message": lines[-1] if lines else "Error",
        })


def _run_tests() -> list[dict]:
    _ensure_project_in_path()
    tests_dir = str(PROJECT_ROOT / "tests")
    loader = unittest.TestLoader()
    suite = loader.discover(
        start_dir=tests_dir,
        pattern="test_*.py",
        top_level_dir=str(PROJECT_ROOT),
    )
    result = _CollectingResult()
    suite.run(result)
    return result.collected


class HealthPage:

    def __init__(self, page: ft.Page):
        self.page = page
        self._results_column = ft.Column(
            spacing=6,
            scroll=ft.ScrollMode.AUTO,
        )
        self._summary_text = ft.Text(
            "",
            size=15,
            weight=ft.FontWeight.W_500,
        )
        self._run_button = ft.Button(
            content=ft.Text("Run Tests"),
            on_click=self._on_run_click,
        )
        self._progress = ft.ProgressRing(
            visible=False,
            width=22,
            height=22,
            stroke_width=3,
        )

    def build(self) -> ft.Column:
        return ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Text(
                    "Health Check",
                    size=34,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Text(
                    "Runs automated tests to verify the app's core logic.",
                    size=15,
                    color=ft.Colors.GREY_700,
                ),
                ft.Divider(),
                ft.Row(
                    spacing=16,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        self._run_button,
                        self._progress,
                        self._summary_text,
                    ],
                ),
                ft.Divider(),
                self._results_column,
            ],
        )

    def _on_run_click(self, e):
        self._run_button.disabled = True
        self._progress.visible = True
        self._summary_text.value = "Running..."
        self._summary_text.color = ft.Colors.GREY_600
        self._results_column.controls.clear()
        self.page.update()
        threading.Thread(target=self._execute, daemon=True).start()

    def _execute(self):
        try:
            collected = _run_tests()
        except Exception as exc:
            collected = []
            self._summary_text.value = f"Runner error: {exc}"
            self._summary_text.color = ft.Colors.RED_700
            self._run_button.disabled = False
            self._progress.visible = False
            self.page.update()
            return

        passed = sum(1 for r in collected if r["status"] == "pass")
        failed = sum(1 for r in collected if r["status"] in ("fail", "error"))
        total = len(collected)

        # Group results by test class
        groups: dict[str, list[dict]] = {}
        for r in collected:
            groups.setdefault(r["class"], []).append(r)

        controls = []
        for class_name, tests in groups.items():
            group_passed = all(t["status"] == "pass" for t in tests)
            controls.append(
                ft.Text(
                    class_name,
                    size=14,
                    weight=ft.FontWeight.BOLD,
                    color=(
                        ft.Colors.GREEN_800
                        if group_passed
                        else ft.Colors.RED_800
                    ),
                )
            )
            for t in tests:
                is_pass = t["status"] == "pass"
                icon = "✓" if is_pass else "✗"
                color = ft.Colors.GREEN_700 if is_pass else ft.Colors.RED_700
                bg = ft.Colors.GREEN_50 if is_pass else ft.Colors.RED_50

                row_controls = [
                    ft.Text(
                        f"  {icon}  {t['name']}",
                        size=13,
                        color=color,
                    )
                ]
                if t.get("message"):
                    row_controls.append(
                        ft.Text(
                            f"       {t['message']}",
                            size=11,
                            color=ft.Colors.RED_600,
                        )
                    )

                controls.append(
                    ft.Container(
                        padding=ft.Padding(left=12, right=12, top=5, bottom=5),
                        border_radius=6,
                        bgcolor=bg,
                        content=ft.Column(
                            spacing=2,
                            controls=row_controls,
                        ),
                    )
                )

            controls.append(ft.Container(height=8))

        self._results_column.controls = controls

        if failed == 0:
            self._summary_text.value = f"All {total} tests passed."
            self._summary_text.color = ft.Colors.GREEN_700
        else:
            self._summary_text.value = (
                f"{passed} passed · {failed} failed · {total} total"
            )
            self._summary_text.color = ft.Colors.RED_700

        self._run_button.disabled = False
        self._progress.visible = False
        self.page.update()
