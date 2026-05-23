from pathlib import Path
import subprocess
import sys
import os

import flet as ft


IMPORTS_PATH = (
    Path("data/imports")
)


class ImportPage:

    def __init__(
        self,
        page: ft.Page,
    ):

        self.page = page

        self.status_text = ft.Text()

        self.file_dropdown = (
            ft.Dropdown(
                width=500,
            )
        )

        self.refresh_files()

    def build(self):

        return ft.Column(
            controls=[
                ft.Text(
                    "Import Bank File",
                    size=32,
                    weight=(
                        ft.FontWeight.BOLD
                    ),
                ),
                ft.Text(
                    (
                        "Place XLSX bank files "
                        "inside the imports folder"
                    ),
                ),
                ft.Divider(),
                ft.Row(
                    controls=[
                        ft.Button(
                            content=ft.Text(
                                "Open Imports Folder"
                            ),
                            on_click=(
                                self.open_imports_folder
                            ),
                        ),
                        ft.Button(
                            content=ft.Text(
                                "Refresh Files"
                            ),
                            on_click=(
                                self.refresh_button_click
                            ),
                        ),
                    ]
                ),
                self.file_dropdown,
                ft.Button(
                    content=ft.Text(
                        "Run Import"
                    ),
                    on_click=self.run_import,
                ),
                self.status_text,
            ]
        )

    def refresh_files(self):

        IMPORTS_PATH.mkdir(
            parents=True,
            exist_ok=True,
        )

        files = sorted(
            IMPORTS_PATH.glob(
                "*.xlsx"
            )
        )

        self.file_dropdown.options = [
            ft.dropdown.Option(
                file.name
            )
            for file in files
        ]

        if files:

            self.file_dropdown.value = (
                files[0].name
            )

    def open_imports_folder(
        self,
        e,
    ):

        IMPORTS_PATH.mkdir(
            parents=True,
            exist_ok=True,
        )

        absolute_path = (
            IMPORTS_PATH.resolve()
        )

        os.startfile(
            absolute_path
        )

    def refresh_button_click(
        self,
        e,
    ):

        self.refresh_files()

        self.status_text.value = (
            "File list refreshed"
        )

        self.page.update()

    def run_import(
        self,
        e,
    ):

        if not self.file_dropdown.value:

            self.status_text.value = (
                "No file selected"
            )

            self.page.update()

            return

        try:

            subprocess.run(
                [
                    sys.executable,
                    "run_import_pipeline.py",
                ],
                check=True,
            )

            subprocess.run(
                [
                    sys.executable,
                    (
                        "run_normalization_pipeline.py"
                    ),
                    "--rebuild-silver",
                ],
                check=True,
            )

            self.status_text.value = (
                (
                    "Import completed "
                    "successfully"
                )
            )

        except Exception as error:

            self.status_text.value = (
                f"Error: {error}"
            )

        self.page.update()