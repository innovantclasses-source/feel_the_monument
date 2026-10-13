import sys
sys.setrecursionlimit(10000)

from setuptools import setup

APP = ['main_window.py']
DATA_FILES = ['assets']
OPTIONS = {
    'argv_emulation': False,
    'packages': ['PyQt6', 'cv2', 'trimesh', 'scipy', 'numpy',
                 'qrcode', 'timm', 'PIL', 'torch', 'torchvision'],
    'excludes': ['torch.testing'],
    'plist': {
        'CFBundleName': 'Feel the Monument',
        'CFBundleDisplayName': 'Feel the Monument',
        'CFBundleIdentifier': 'com.feelthemonument.app',
        'CFBundleVersion': '1.0.0',
        'NSHighResolutionCapable': True,
    }
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)