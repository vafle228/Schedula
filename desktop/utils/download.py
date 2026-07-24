import urllib.request

import webview


class DownloadApi:
    def __init__(self):
        self._window: webview.Window | None = None

    @property
    def window(self) -> webview.Window:
        if self._window is None:
            raise ValueError("Window not initialized")
        return self._window

    @window.setter
    def window(self, value: webview.Window) -> None:
        self._window = value

    def initiate_download(self, url: str, default_filename: str) -> dict:
        result = self.window.create_file_dialog(
            directory="",
            save_filename=default_filename,
            dialog_type=webview.FileDialog.SAVE,
        )

        if result:
            save_path = result[0]
            try:
                urllib.request.urlretrieve(url, save_path)
                return {"status": "success", "path": save_path}
            except Exception as e:
                return {"status": "error", "message": str(e)}

        return {"status": "cancelled"}