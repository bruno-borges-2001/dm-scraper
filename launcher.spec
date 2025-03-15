# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.utils.hooks import copy_metadata
import os

base_url = os.environ.get('PYTHON_PATH') or 'venv/lib/python3.12'
print("Loading from", base_url)

import_modules = [
    'streamlit',
]

datas = [("./src", "./src")]

for module in import_modules:
    datas += (base_url + "/site-packages/" + module, "./" + module),
    datas += collect_data_files(module)
    datas += copy_metadata(module)

hiddenimports=[
    'chromedriver_autoinstaller',
    'playwright._impl._driver',
    'playwright.async_api',
    'playwright.sync_api',
    'webdriver_manager',
    'webdriver_manager.chrome',
    'selenium',
    'selenium.commom',
    'selenium.commom.exceptions',
    'selenium.webdriver',
    'selenium.webdriver.common',
    'selenium.webdriver.common.by',
    'selenium.webdriver.support',
    'selenium.webdriver.support.wait',
    'selenium.webdriver.support.expected_conditions',
    'selenium.webdriver.chrome',
    'selenium.webdriver.chrome.service',
    'selenium.webdriver.chrome.options',
    'pandas'
]

block_cipher = None

a = Analysis(
    ['launcher.py'],
    pathex=["."],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='dm-scraper',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
