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


def copy_resources():
    print("== resources ==")
    res = os.path.join(OUT, "resources")
    if os.path.isdir(res):
        shutil.rmtree(res)
    os.makedirs(res)
    for name in RES:
        src = os.path.join(HERE, name)
        if not os.path.exists(src):
            if name in REQUIRED:
                raise SystemExit("thiếu tài nguyên bắt buộc: %s" % name)
            print("   bỏ qua (chưa có): %s" % name)
            continue
        dst = os.path.join(res, name)
        if name == "audio":
            # chỉ chép audio của đề thật sự có trong exams.json — repo giữ cả file
            # của đề chưa nhập xong, không cần nhét vào bản phát hành
            ids = {e["id"] for e in json.load(
                open(os.path.join(HERE, "exams.json"), encoding="utf-8"))}
            shutil.copytree(src, dst, ignore=lambda d, names: [
                n for n in names
                if os.path.isdir(os.path.join(d, n)) and d == src and n not in ids])
            n = sum(len(f) for _, _, f in os.walk(dst))
            print("   %-14s %d file (đề: %s)" % (name + "/", n, ", ".join(sorted(ids))))
            continue
        if os.path.isdir(src):
            shutil.copytree(src, dst)
            n = sum(len(f) for _, _, f in os.walk(dst))
            print("   %-14s %d file" % (name + "/", n))
        else:
            shutil.copy2(src, dst)
            print("   %-14s %.1f KB" % (name, os.path.getsize(dst) / 1024))


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
