from autogen_ext.agents.file_surfer import FileSurfer

from ._secured_markdown_file_browser import SecuredMarkdownFileBrowser


class SecuredFileSurfer(FileSurfer):
    def __init__(
        self,
        name: str,
        model_client,
    ) -> None:
        super().__init__(name, model_client)
        self._browser = SecuredMarkdownFileBrowser(viewport_size=1024 * 5)
