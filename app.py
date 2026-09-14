# -*- coding: utf-8 -*-
"""GunGun N3 Trainer - desktop host (pywebview + WebView2)."""
import base64
import ctypes
import datetime
import json
import os
import subprocess
import sys
import threading
import time
import winreg

import pystray
import webview
from PIL import Image

APP_NAME = "GunGun N3 Trainer"
STORAGE_DIR = os.path.join(
    os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "GunGunN3Trainer"
)
RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
RUN_NAME = "GunGunN3Trainer"
# PowerShell's registered AppUserModelID: toasts from it are always displayed,
# no Start-Menu shortcut registration needed for an unpackaged app
PS_APPID = r"{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}\WindowsPowerShell\v1.0\powershell.exe"

# a second launch drops this file; the running instance picks it up and un-hides
SHOW_FLAG = os.path.join(STORAGE_DIR, "show.request")
# the user's own Claude API key, kept out of the progress backup on purpose
API_KEY_FILE = os.path.join(STORAGE_DIR, "claude-api-key.txt")
# Sonnet + effort medium: chấm dịch N3 không cần tới Opus, mà rẻ hơn ~2,5 lần
# (sonnet-5 $2/$10 mỗi triệu token, opus-5 $5/$25)
_ai = {"model": "claude-sonnet-5"}

_reminders = {"times": [], "fired": {}}
# how many goal sessions the user still owes, pushed from the UI
_makeup = {"total": 0, "days": 0, "notified": None}
# window/tray runtime state
_ui = {"window": None, "tray": None, "quitting": False,
       "close_action": "ask", "tray_hint_shown": False}


RES_FILES = ("vocab.json", "kanji.json", "grammar.json", "reading.json", "exams.json",
             "icon.ico", os.path.join("web", "index.html"))


def res_base():
    """Thư mục tài nguyên (web/, *.json, audio/, icon.ico).

    Bản đóng gói: `resources/` nằm cạnh exe — exe chỉ chứa runtime nên nhẹ và
    không phải build lại mỗi khi đổi dữ liệu. Có `_MEIPASS` là bản cũ nhúng sẵn
    tài nguyên vào exe, vẫn chạy được. Chạy từ source thì lấy luôn thư mục repo.
    """
    if getattr(sys, "frozen", False):
        ext = os.path.join(os.path.dirname(sys.executable), "resources")
        if os.path.isdir(ext):
            return ext
        return getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


def res_path(rel):
    return os.path.join(res_base(), rel)


def _check_resources():
    """Thiếu tài nguyên thì báo rõ — bản --windowed không có console để in lỗi."""
    missing = [r for r in RES_FILES if not os.path.isfile(res_path(r))]
    if not missing:
        return True
    ctypes.windll.user32.MessageBoxW(
        None,
        "Không tìm thấy tài nguyên:\n\n  " + "\n  ".join(missing)
        + "\n\nThư mục đang tìm:\n  " + res_base()
        + "\n\nGiải nén đầy đủ cả thư mục 'resources' cạnh file exe rồi mở lại.",
        APP_NAME, 0x10)
    return False


def _app_exe():
    return sys.executable if getattr(sys, "frozen", False) else None


def _autostart_get():
    """-> {'enabled': bool, 'hidden': bool}"""
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as k:
            val, _ = winreg.QueryValueEx(k, RUN_NAME)
        return {"enabled": True, "hidden": "--tray" in str(val)}
    except OSError:
        return {"enabled": False, "hidden": False}


def _autostart_set(enabled, hidden=False):
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as k:
            if enabled:
                exe = _app_exe()
                if not exe:
                    return False
                cmd = f'"{exe}" --tray' if hidden else f'"{exe}"'
                winreg.SetValueEx(k, RUN_NAME, 0, winreg.REG_SZ, cmd)
            else:
                try:
                    winreg.DeleteValue(k, RUN_NAME)
                except OSError:
                    pass
        return True
    except OSError:
        return False


def show_toast(title, body):
    """Windows toast notification via a hidden PowerShell process (no extra deps)."""
    def q(s):
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("'", "''")
    xml = ('<toast duration="long"><visual><binding template="ToastGeneric">'
           f"<text>{q(title)}</text><text>{q(body)}</text></binding></visual>"
           '<audio src="ms-winsoundevent:Notification.Reminder"/></toast>')
    script = (
        "$null=[Windows.UI.Notifications.ToastNotificationManager,Windows.UI.Notifications,ContentType=WindowsRuntime];"
        "$null=[Windows.UI.Notifications.ToastNotification,Windows.UI.Notifications,ContentType=WindowsRuntime];"
        "$null=[Windows.Data.Xml.Dom.XmlDocument,Windows.Data.Xml.Dom.XmlDocument,ContentType=WindowsRuntime];"
        "$x=New-Object Windows.Data.Xml.Dom.XmlDocument;"
        f"$x.LoadXml('{xml}');"
        "$t=New-Object Windows.UI.Notifications.ToastNotification $x;"
        f"[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('{PS_APPID}').Show($t)"
    )
    enc = base64.b64encode(script.encode("utf-16-le")).decode()
    try:
        subprocess.Popen(
            ["powershell", "-NoProfile", "-NonInteractive", "-EncodedCommand", enc],
            creationflags=0x08000000,  # CREATE_NO_WINDOW
            # a --windowed build has no stdio handles to inherit
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except OSError:
        pass


def _reminder_loop():
    while True:
        now = datetime.datetime.now()
        hm = now.strftime("%H:%M")
        day = now.strftime("%Y-%m-%d")
        for t in list(_reminders["times"]):
            if t == hm and _reminders["fired"].get(t) != day:
                _reminders["fired"][t] = day
                if _makeup["total"] > 0:
                    body = (f"Đến giờ học rồi! Bạn đang nợ {_makeup['total']} session "
                            f"của {_makeup['days']} ngày — học bù hôm nay nhé 🎌")
                else:
                    body = "Đến giờ học tiếng Nhật rồi! 今日も頑張りましょう 🎌"
                show_toast("GunGun N3 Trainer", body)
        time.sleep(15)


def _load_saved_reminders():
    try:
        with open(os.path.join(STORAGE_DIR, "state-backup.json"), encoding="utf-8") as f:
            st = json.load(f)
        times = (st.get("settings") or {}).get("remindTimes") or []
        _reminders["times"] = [t for t in times if isinstance(t, str) and len(t) == 5]
    except (OSError, ValueError):
        pass


def _show_window():
    w = _ui["window"]
    if not w:
        return
    try:
        w.show()
        w.restore()
        w.on_top = True
        w.on_top = False
    except Exception:
        pass


def _hide_window():
    w = _ui["window"]
    if not w:
        return
    try:
        w.hide()
    except Exception:
        return
    if not _ui["tray_hint_shown"]:
        _ui["tray_hint_shown"] = True
        show_toast("GunGun N3 Trainer",
                   "App vẫn chạy ngầm ở khay hệ thống để nhắc bạn học. "
                   "Nhấn biểu tượng 語 cạnh đồng hồ để mở lại.")


def _quit_app():
    _ui["quitting"] = True
    tray = _ui["tray"]
    if tray:
        try:
            tray.stop()
        except Exception:
            pass
    w = _ui["window"]
    if w:
        try:
            w.destroy()
        except Exception:
            os._exit(0)


def _start_tray():
    try:
        img = Image.open(res_path("icon.ico"))
    except OSError:
        img = Image.new("RGBA", (64, 64), (79, 70, 229, 255))
    menu = pystray.Menu(
        pystray.MenuItem("Mở GunGun N3 Trainer",
                         lambda *_: _show_window(), default=True),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Thoát hẳn", lambda *_: _quit_app()),
    )
    icon = pystray.Icon("GunGunN3Trainer", img, "GunGun N3 Trainer", menu)
    _ui["tray"] = icon
    threading.Thread(target=icon.run, daemon=True).start()


def _show_watch_loop():
    while True:
        try:
            if os.path.exists(SHOW_FLAG):
                os.remove(SHOW_FLAG)
                _show_window()
        except OSError:
            pass
        time.sleep(1)


def _on_closing():
    """X button: quit, minimise to tray, or ask the UI - per saved preference."""
    if _ui["quitting"] or _ui["close_action"] == "quit":
        return None                      # let the window close
    if _ui["close_action"] == "tray":
        threading.Thread(target=_hide_window, daemon=True).start()
    else:
        # evaluate_js must not run on the GUI thread that is handling this event
        threading.Thread(
            target=lambda: _ui["window"].evaluate_js("App.askCloseAction()"),
            daemon=True).start()
    return False                         # cancel the close


def _load_close_pref():
    try:
        with open(os.path.join(STORAGE_DIR, "state-backup.json"), encoding="utf-8") as f:
            st = json.load(f)
        a = (st.get("settings") or {}).get("closeAction")
        if a in ("ask", "tray", "quit"):
            _ui["close_action"] = a
    except (OSError, ValueError):
        pass


class Api:
    def get_data(self):
        out = {}
        for name in ("vocab", "kanji", "grammar", "reading", "exams"):
            with open(res_path(name + ".json"), encoding="utf-8") as f:
                out[name] = json.load(f)
        return out

    # ---- Claude-powered translation grading -------------------------------
    def get_api_key(self):
        try:
            with open(API_KEY_FILE, encoding="utf-8") as f:
                k = f.read().strip()
            return {"set": bool(k), "tail": k[-4:] if k else ""}
        except OSError:
            return {"set": False, "tail": ""}

    def set_api_key(self, key):
        key = (key or "").strip()
        try:
            os.makedirs(STORAGE_DIR, exist_ok=True)
            if key:
                with open(API_KEY_FILE, "w", encoding="utf-8") as f:
                    f.write(key)
            elif os.path.exists(API_KEY_FILE):
                os.remove(API_KEY_FILE)
            return True
        except OSError:
            return False

    def grade_translation(self, payload):
        """Grade a Japanese -> Vietnamese translation on meaning, not wording."""
        try:
            with open(API_KEY_FILE, encoding="utf-8") as f:
                key = f.read().strip()
        except OSError:
            key = ""
        if not key:
            return {"ok": False, "error": "no_key"}
        try:
            import anthropic
        except ImportError:
            return {"ok": False, "error": "no_sdk"}

        jp = payload.get("jp", "")
        user = payload.get("user", "")
        pattern = payload.get("pattern", "")
        meaning = payload.get("meaning", "")
        notes = " ".join(payload.get("notes") or [])[:700]

        system = (
            "Bạn là giáo viên tiếng Nhật người Việt, chấm bài dịch Nhật→Việt cho học viên trình độ JLPT N3.\n"
            "Nguyên tắc chấm:\n"
            "- Chấm theo NGHĨA, không bắt trùng khớp từng chữ. Nhiều cách diễn đạt khác nhau đều có thể đúng.\n"
            "- Chỉ trừ điểm khi: sai nghĩa, bỏ sót ý quan trọng, hiểu sai mẫu ngữ pháp, sai sắc thái/chủ ngữ, hoặc thêm ý không có.\n"
            "- Câu tiếng Việt tự nhiên, thoát ý mà vẫn đúng nghĩa thì cho điểm cao.\n"
            "- Lỗi chính tả nhỏ hoặc thiếu dấu câu chỉ trừ rất ít.\n"
            "score: 90-100 rất tốt, 70-89 đúng ý nhưng còn vụng, 40-69 hiểu sai một phần, 0-39 sai hoặc bỏ trống.\n"
            "correct = true khi score >= 70.\n"
            "feedback: nhận xét NGẮN bằng tiếng Việt (1-3 câu), nói rõ đúng chỗ nào, sai/thiếu chỗ nào.\n"
            "grammar_note: 1 câu giải thích mẫu ngữ pháp được dùng trong câu này.\n"
            "suggested: một bản dịch mẫu tự nhiên bằng tiếng Việt."
        )
        prompt = (
            f"Mẫu ngữ pháp đang học: {pattern}\n"
            f"Ý nghĩa mẫu: {meaning}\n"
            f"Ghi chú sách: {notes}\n\n"
            f"Câu tiếng Nhật cần dịch: {jp}\n"
            f"Bản dịch của học viên: {user or '(bỏ trống)'}"
        )
        schema = {
            "type": "object",
            "properties": {
                "score": {"type": "integer"},
                "correct": {"type": "boolean"},
                "feedback": {"type": "string"},
                "grammar_note": {"type": "string"},
                "suggested": {"type": "string"},
            },
            "required": ["score", "correct", "feedback", "grammar_note", "suggested"],
            "additionalProperties": False,
        }
        try:
            client = anthropic.Anthropic(api_key=key, timeout=60.0, max_retries=1)
            resp = client.messages.create(
                model=_ai["model"],
                # Trần chứ không phải mức tiêu: chỉ trả tiền số token thực sinh ra.
                # Để rộng vì effort medium suy nghĩ nhiều hơn — chạm trần là JSON bị
                # cắt giữa chừng, json.loads nổ, mất tiền mà không có kết quả.
                max_tokens=4000,
                system=system,
                output_config={"effort": "medium",
                               "format": {"type": "json_schema", "schema": schema}},
                messages=[{"role": "user", "content": prompt}],
            )
            if resp.stop_reason == "max_tokens":
                return {"ok": False, "error": "truncated"}
            text = next(b.text for b in resp.content if b.type == "text")
            data = json.loads(text)
            data["ok"] = True
            data["source"] = "ai"
            return data
        except Exception as e:                      # noqa: BLE001 - surfaced in the UI
            name = type(e).__name__
            if "Authentication" in name or "PermissionDenied" in name:
                return {"ok": False, "error": "bad_key"}
            if "RateLimit" in name:
                return {"ok": False, "error": "rate_limit"}
            if "Connection" in name or "Timeout" in name:
                return {"ok": False, "error": "offline"}
            return {"ok": False, "error": "%s: %s" % (name, str(e)[:200])}

    # Mirror of localStorage state, so progress survives a WebView2 profile wipe.
    # Written atomically: a crash mid-write can never corrupt the existing backup.
    def save_backup(self, text):
        try:
            os.makedirs(STORAGE_DIR, exist_ok=True)
            tmp = os.path.join(STORAGE_DIR, "state-backup.json.tmp")
            with open(tmp, "w", encoding="utf-8") as f:
                f.write(text)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, os.path.join(STORAGE_DIR, "state-backup.json"))
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

    def get_autostart(self):
        return _autostart_get()

    def set_autostart(self, enabled, hidden=False):
        return _autostart_set(bool(enabled), bool(hidden))

    def set_reminders(self, times):
        _reminders["times"] = [
            t for t in (times or []) if isinstance(t, str) and len(t) == 5
        ]
        return True

    def set_makeup(self, total, days):
        _makeup["total"] = int(total or 0)
        _makeup["days"] = int(days or 0)
        today = datetime.date.today().isoformat()
        # one automatic nudge per day when the user has catching up to do
        if _makeup["total"] > 0 and _makeup["notified"] != today:
            _makeup["notified"] = today
            threading.Timer(8, lambda: show_toast(
                "GunGun N3 Trainer",
                f"Bạn đang nợ {_makeup['total']} session của {_makeup['days']} ngày chưa đạt "
                "mục tiêu. Học bù hôm nay để tô đậm lại những ngày đó nhé! 📚")).start()
        elif _makeup["total"] == 0:
            _makeup["notified"] = None
        return True

    def set_close_pref(self, action):
        if action in ("ask", "tray", "quit"):
            _ui["close_action"] = action
        return True

    def close_choice(self, action):
        """Called by the close dialog in the UI."""
        if action == "quit":
            threading.Thread(target=_quit_app, daemon=True).start()
        else:
            threading.Thread(target=_hide_window, daemon=True).start()
        return True

    def test_notification(self):
        show_toast("GunGun N3 Trainer",
                   "Thông báo hoạt động tốt! Đây là nhắc nhở giờ học của bạn 🔔")
        return True


if __name__ == "__main__":
    # single instance only: two WebView2 processes sharing one profile folder
    # fight over the storage lock and progress can silently stop being saved
    ctypes.windll.kernel32.CreateMutexW(None, False, "GunGunN3Trainer_SingleInstance")
    if ctypes.windll.kernel32.GetLastError() == 183:  # ERROR_ALREADY_EXISTS
        # already running (possibly hidden in the tray): ask it to come forward
        try:
            os.makedirs(STORAGE_DIR, exist_ok=True)
            open(SHOW_FLAG, "w").close()
        except OSError:
            pass
        sys.exit(0)
    if not _check_resources():
        sys.exit(1)
    os.makedirs(STORAGE_DIR, exist_ok=True)
    try:
        os.remove(SHOW_FLAG)          # clear a stale request from a past run
    except OSError:
        pass
    # keep the autostart entry pointing at wherever the exe currently lives
    _as = _autostart_get()
    if _as["enabled"]:
        _autostart_set(True, _as["hidden"])
    _load_saved_reminders()
    _load_close_pref()
    threading.Thread(target=_reminder_loop, daemon=True).start()
    threading.Thread(target=_show_watch_loop, daemon=True).start()
    start_hidden = "--tray" in sys.argv
    window = webview.create_window(
        APP_NAME,
        res_path(os.path.join("web", "index.html")),
        js_api=Api(),
        width=1120,
        height=780,
        min_size=(900, 640),
        hidden=start_hidden,
    )
    _ui["window"] = window
    _ui["tray_hint_shown"] = start_hidden
    window.events.closing += _on_closing
    _start_tray()
    webview.start(private_mode=False, storage_path=STORAGE_DIR)
    _quit_app()
