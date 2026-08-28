# -*- coding: utf-8 -*-
"""GunGun N3 Trainer - desktop host (pywebview + WebView2)."""
import json
import os
import sys

import webview

APP_NAME = "GunGun N3 Trainer"
STORAGE_DIR = os.path.join(
    os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "GunGunN3Trainer"
)


def res_path(rel):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel)


class Api:
    def get_data(self):
        with open(res_path("vocab.json"), encoding="utf-8") as f:
            vocab = json.load(f)
        with open(res_path("kanji.json"), encoding="utf-8") as f:
            kanji = json.load(f)
        return {"vocab": vocab, "kanji": kanji}

    # Mirror of localStorage state, so progress survives a WebView2 profile wipe.
    def save_backup(self, text):
        try:
            os.makedirs(STORAGE_DIR, exist_ok=True)
            with open(
                os.path.join(STORAGE_DIR, "state-backup.json"), "w", encoding="utf-8"
            ) as f:
                f.write(text)
            return True
        except OSError:
            return False

    def load_backup(self):
        try:
            with open(
                os.path.join(STORAGE_DIR, "state-backup.json"), encoding="utf-8"
            ) as f:
                return f.read()
        except OSError:
            return None


if __name__ == "__main__":
    os.makedirs(STORAGE_DIR, exist_ok=True)
    webview.create_window(
        APP_NAME,
        res_path(os.path.join("web", "index.html")),
        js_api=Api(),
        width=1120,
        height=780,
        min_size=(900, 640),
    )
    webview.start(private_mode=False, storage_path=STORAGE_DIR)
