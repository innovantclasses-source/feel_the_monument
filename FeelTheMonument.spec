import sys
from PyInstaller.utils.hooks import collect_all, collect_submodules

block_cipher = None

timm_datas, timm_binaries, timm_hiddenimports = collect_all('timm')
torch_datas, torch_binaries, torch_hiddenimports = collect_all('torch')
tv_datas, tv_binaries, tv_hiddenimports = collect_all('torchvision')

a = Analysis(
    ['main_window.py'],
    pathex=['.'],
    binaries=timm_binaries + torch_binaries + tv_binaries,
    datas=[
        ('assets', 'assets'),
        ('depth_engine.py', '.'),
        ('stl_generator.py', '.'),
        ('braille_engine.py', '.'),
        ('qr_generator.py', '.'),
    ] + timm_datas + torch_datas + tv_datas,
    hiddenimports=[
        'depth_engine',
        'stl_generator',
        'braille_engine',
        'qr_generator',
        'torch',
        'torchvision',
        'timm',
        'timm.models',
        'timm.models.layers',
        'timm.models.helpers',
        'timm.models.vision_transformer',
        'timm.models.resnet',
        'timm.data',
        'timm.loss',
        'timm.optim',
        'timm.scheduler',
        'cv2',
        'numpy',
        'scipy',
        'scipy.ndimage',
        'trimesh',
        'qrcode',
        'PIL',
    ] + timm_hiddenimports + torch_hiddenimports + tv_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='FeelTheMonument',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='FeelTheMonument',
)

app = BUNDLE(
    coll,
    name='FeelTheMonument.app',
    icon=None,
    bundle_identifier='com.feelthemonument.app',
)
