# AstroMapper.spec
# 빌드 명령: pyinstaller AstroMapper.spec

block_cipher = None

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        # 리소스 파일들
        ('res/images/*', 'res/images'),
        ('res/images/icons/*', 'res/images/icons'),
        ('res/data/*.json', 'res/data'),
        
        # 설정 파일들
        ('src/config/default_config.yaml', 'src/config'),
        ('src/config/settings.json', 'src/config'),
        ('src/config/default_settings.json', 'src/config'),
        
        # 스타일 파일들
        ('src/ui/styles.qss', 'src/ui'),
        ('src/ui/styles/*.qss', 'src/ui/styles'),
        ('src/ui/styles/message_box/*.qss', 'src/ui/styles/message_box'),
        
        # UI 관련 파일들
        ('src/ui/widgets/**/*', 'src/ui/widgets'),
        ('src/ui/dialogs/**/*', 'src/ui/dialogs'),
        
    ],
    hiddenimports=[
        'src.core.roi',
        'src.core.image',
        'src.utils',
        'src.utils.config',
        'src.utils.helper',
        'src.utils.settings',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['__pycache__'],  # __pycache__ 제외
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='AstroMapper',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # False로 하면 콘솔창 없이 GUI만
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AstroMapper'
) 