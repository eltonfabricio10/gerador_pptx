# -*- coding: utf-8 -*-
import subprocess
import platform
import ctypes
from ctypes.wintypes import MAX_PATH
from pathlib import Path

if platform.system() == "Linux":
    documents = subprocess.check_output(
        ["xdg-user-dir", "DOCUMENTS"],
        text=True
    ).strip()

elif platform.system() == "Windows":
    CSIDL_PERSONAL = 0x0005  # My Documents
    buf = ctypes.create_unicode_buffer(MAX_PATH + 1)
    result = ctypes.windll.shell32.SHGetSpecialFolderPathW(
        None, buf, CSIDL_PERSONAL, False
    )
    documents = buf.value if result else None

else:
    documents = Path.home() / 'Documents'
