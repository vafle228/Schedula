import urllib.request

import webview


class DownloadApi:
    # pywebview builds the JS bridge by walking every *public* attribute of the
    # js_api object (webview/util.py get_functions) and recursing into any
    # non-callable one. A public Window attribute makes it descend into Qt's
    # native object graph forever (window.native.AccessibilityObject.Bounds...),
    # which spams errors and stalls window init. Underscore names are skipped.
    def __init__(self):
        self.window: webview.Window | None = None

    def initiate_download(self, url: str, default_filename: str) -> dict:
        if self.window is None:
            raise ValueError("Window not initialized")

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