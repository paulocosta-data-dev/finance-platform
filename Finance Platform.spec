# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['flet_app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('app/category/rules/category_rules.yaml', 'app/category/rules'),
        ('app/semantic/rules/semantic_rules.yaml', 'app/semantic/rules'),
        ('app/merchant/rules/merchant_rules.yaml', 'app/merchant/rules'),
        ('app/cashflow/config/forecast_groups.yaml', 'app/cashflow/config'),
        ('app/semantic/entities/entity_registry.yaml', 'app/semantic/entities'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Finance Platform',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='C:\\Users\\pdcge\\AppData\\Local\\Temp\\f93e2011-d7aa-4314-93b0-2a61a346304e',
)
