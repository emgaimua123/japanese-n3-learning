# -*- coding: utf-8 -*-
"""Đóng gói GunGun N3 Trainer: exe chỉ chứa runtime, tài nguyên để ngoài.

    python build.py

Kết quả: dist/GunGunN3Trainer/
    GunGunN3Trainer.exe      ~35 MB, chỉ có Python + pywebview + pystray
    resources/               web/, 5 file JSON, icon.ico, audio/

Đổi dữ liệu (exams.json, audio, index.html…) thì chỉ cần chép đè vào
resources/, KHÔNG phải build lại exe. Phát hành thì nén cả thư mục
dist/GunGunN3Trainer thành zip.
"""
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "dist", "GunGunN3Trainer")
EXE = os.path.join(OUT, "GunGunN3Trainer.exe")
# thư mục / file được chép vào resources/
RES = ["web", "audio", "images", "vocab.json", "kanji.json", "grammar.json",
       "reading.json", "exams.json", "icon.ico"]
# 5 JSON này thiếu là app không chạy nổi
REQUIRED = ["web", "vocab.json", "kanji.json", "grammar.json", "reading.json",
            "exams.json", "icon.ico"]


def build_exe():
    print("== PyInstaller ==")
    # dùng đường dẫn tuyệt đối: --specpath làm PyInstaller đổi gốc của đường dẫn tương đối
    cmd = [sys.executable, "-m", "PyInstaller", "--noconfirm", "--onefile",
           "--windowed", "--name", "GunGunN3Trainer",
           "--icon", os.path.join(HERE, "icon.ico"),
           "--distpath", os.path.join(HERE, "build", "exe"),
           "--workpath", os.path.join(HERE, "build", "work"),
           "--specpath", os.path.join(HERE, "build"),
           "--hidden-import", "pystray._win32", os.path.join(HERE, "app.py")]
    subprocess.check_call(cmd, cwd=HERE)


def sync_file(src, dst):
    """Chép nếu khác, trả True nếu có chép. So theo cỡ + thời gian sửa."""
    if os.path.isfile(dst):
        a, b = os.stat(src), os.stat(dst)
        if a.st_size == b.st_size and abs(a.st_mtime - b.st_mtime) < 2:
            return False
    d = os.path.dirname(dst)
    if d and not os.path.isdir(d):
        os.makedirs(d)
    shutil.copy2(src, dst)
    return True


def sync_dir(src, dst, keep=None):
    """Đồng bộ thư mục tại chỗ: chép file đổi, xoá file thừa.

    `keep` (nếu có) là tập thư mục con được giữ, còn lại bỏ qua.
    """
    n = skip = 0
    want = set()
    for root, dirs, files in os.walk(src):
        rel = os.path.relpath(root, src)
        if keep is not None and rel != ".":
            top = rel.split(os.sep)[0]
            if top not in keep:
                dirs[:] = []
                continue
        for f in files:
            if f.endswith(".md"):      # ghi chú cho người sửa repo, exe không cần
                continue
            r = os.path.normpath(os.path.join(rel, f))
            want.add(r)
            if sync_file(os.path.join(root, f), os.path.join(dst, r)):
                n += 1
            else:
                skip += 1
    for root, _, files in os.walk(dst):
        for f in files:
            r = os.path.relpath(os.path.join(root, f), dst)
            if os.path.normpath(r) not in want:
                os.remove(os.path.join(root, f))
    return n, skip


def copy_resources():
    """Đồng bộ TẠI CHỖ, không xoá cả thư mục rồi chép lại.

    Cách cũ `rmtree` + `copytree` để hở một quãng vài giây thư mục resources
    trống: mở app đúng lúc đó là `_check_resources()` báo thiếu tài nguyên rồi
    thoát. Chép tại chỗ còn nhanh hơn hẳn vì 121 MB audio hầu như không đổi, và
    không đụng vào file đang bị app mở (icon.ico) nên cập nhật được cả khi app
    đang chạy.
    """
    print("== resources ==")
    res = os.path.join(OUT, "resources")
    os.makedirs(res, exist_ok=True)
    for name in RES:
        src = os.path.join(HERE, name)
        if not os.path.exists(src):
            if name in REQUIRED:
                raise SystemExit("thiếu tài nguyên bắt buộc: %s" % name)
            print("   bỏ qua (chưa có): %s" % name)
            continue
        dst = os.path.join(res, name)
        if os.path.isdir(src):
            keep = None
            note = ""
            if name == "audio":
                # chỉ giữ audio của đề thật sự có trong exams.json — repo giữ cả
                # file của đề chưa nhập xong, không cần nhét vào bản phát hành
                keep = {e["id"] for e in json.load(
                    open(os.path.join(HERE, "exams.json"), encoding="utf-8"))}
                note = " (đề: %s)" % ", ".join(sorted(keep))
            n, skip = sync_dir(src, dst, keep)
            print("   %-14s %d file chép, %d giữ nguyên%s" % (name + "/", n, skip, note))
        else:
            print("   %-14s %s" % (name, "đã chép" if sync_file(src, dst) else "giữ nguyên"))


def main():
    if os.path.isfile(EXE):
        try:                                  # exe đang chạy thì Windows khoá file
            os.replace(EXE, EXE + ".old")
            os.remove(EXE + ".old")
        except OSError:
            raise SystemExit(
                "Không ghi đè được %s — đang mở app thì tắt hẳn (kể cả icon ở khay) "
                "rồi chạy lại." % EXE)
    os.makedirs(OUT, exist_ok=True)
    build_exe()
    shutil.copy2(os.path.join(HERE, "build", "exe", "GunGunN3Trainer.exe"), EXE)
    copy_resources()
    total = sum(os.path.getsize(os.path.join(r, f))
                for r, _, fs in os.walk(OUT) for f in fs)
    print("\nxong: %s" % OUT)
    print("   exe %.1f MB · tổng %.1f MB"
          % (os.path.getsize(EXE) / 1048576, total / 1048576))


if __name__ == "__main__":
    main()
