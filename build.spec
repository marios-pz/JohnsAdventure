# -*- mode: python ; coding: utf-8 -*-

import platform

_WINDOWS = "Windows"
_LINUX = "Linux"
_MAC = "Darwin"

host_os = platform.system()

if host_os not in (_WINDOWS, _LINUX, _MAC):
    txt = f"""
    Unrecognized operating system: {host_os}
    Μη αναγνωρισμένο λειτουργικό σύστημα: {host_os}
    """
    raise ValueError(txt)
    
# OS of the host, if its Darwin, Change it to MacOS
host_os = "MacOS (x86_64)" if platform.system() == _MAC else platform.system()

VERSION = "0.23"


print(f"""
Compiling John's Adventures for {host_os}....

Pyinstaller config by @mariopapaz
""")


block_cipher = None


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('data', 'data')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

print("Finished importing the data folder")

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=f"John's Adventure Chapter 1 for {host_os}",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    icon="data/ui/application.ico",
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

app = BUNDLE(exe,
         name=f"John's Adventure Chapter 1",
         icon="data/ui/application.ico",
         bundle_identifier=None)

print("The game has been successfully compiled.")
