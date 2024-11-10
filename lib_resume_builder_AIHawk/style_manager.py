import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional

class StyleManager:
    
    def __init__(self):
        self.styles_directory: Optional[Path] = None

    def set_styles_directory(self, styles_directory: Path):
        self.styles_directory = styles_directory

    def get_styles(self) -> Dict[str, Tuple[str, str]]:
        if self.styles_directory is None:
            print("Styles directory is not set.")
            return {}

        styles_to_files = {}
        try:
            files = os.listdir(self.styles_directory)
            for f in files:
                file_path = self.styles_directory / f
                if file_path.is_file():
                    with open(file_path, 'r', encoding='utf-8') as file:
                        first_line = file.readline().strip()
                        if first_line.startswith("/*") and first_line.endswith("*/"):
                            content = first_line[2:-2].strip()
                            if '$' in content:
                                style_name, author_link = content.split('$', 1)
                                styles_to_files[style_name.strip()] = (f, author_link.strip())
                            else:
                                print(f"Invalid format in file {f}: missing '$' separator.")
        except FileNotFoundError:
            print(f"Directory {self.styles_directory} not found.")
        except PermissionError:
            print(f"Permission denied to access {self.styles_directory}.")
        return styles_to_files

    def format_choices(self, styles_to_files: Dict[str, Tuple[str, str]]) -> List[str]:
        return [f"{style_name} (style author -> {author_link})" for style_name, (_, author_link) in styles_to_files.items()]

    def get_style_path(self, selected_style: str) -> Optional[Path]:
        styles = self.get_styles()
        if selected_style not in styles:
            print(f"Style '{selected_style}' not found.")
            return None

        file_name, _ = styles[selected_style]
        return self.styles_directory / file_name if self.styles_directory else None
