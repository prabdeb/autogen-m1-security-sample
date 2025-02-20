import os
import sys
import time
from typing import Union

from autogen_ext.agents.file_surfer._markdown_file_browser import MarkdownFileBrowser


class SecuredMarkdownFileBrowser(MarkdownFileBrowser):
    def __init__(  # type: ignore
        self, viewport_size: Union[int, None] = 1024 * 8
    ):
        super().__init__(viewport_size)
    
    def _is_safe_path(self, path: str) -> bool:
        # Check if the path is a subdirectory of the current working directory
        # Additionally, we can implement more sophisticated checks if needed
        cwd = os.getcwd()
        return os.path.commonpath([path, cwd]) == cwd

    def set_path(self, path: str) -> None:
        # Handle relative paths
        path = os.path.expanduser(path)
        if not os.path.isabs(path):
            if os.path.isfile(self.path):
                path = os.path.abspath(os.path.join(os.path.dirname(self.path), path))
            elif os.path.isdir(self.path):
                path = os.path.abspath(os.path.join(self.path, path))
            # If neither a file or a directory, take it verbatim
        
        if not self._is_safe_path(path):
            raise ValueError(f"Access to the path {path} is not allowed, TERMINATE the program immediately.")

        self.history.append((path, time.time()))
        self._open_path(path)
        self.viewport_current_page = 0
        self.find_on_page_query = None
        self.find_on_page_viewport = None
