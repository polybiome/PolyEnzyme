# -*- mode: python -*-

block_cipher = None
from kivy.deps import sdl2, glew

a = Analysis(['C:\\Users\\David\\Desktop\\iGEM\\KivyStuff\\MichaelisMentenDemo\\main.py'],
             pathex=['C:\\Users\\David\\Desktop\\iGEM\\KivyStuff\\MichaelisMentenDemo'],
             binaries=None,
             datas=None,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='PolyEnzyme',
          debug=True,
          strip=False,
          upx=True,
          console=True , icon='C:\\Users\\David\\Desktop\\iGEM\\KivyStuff\\MichaelisMentenDemo\\myIco.ico')
coll = COLLECT(exe, Tree('C:\\Users\\David\\Desktop\\iGEM\\KivyStuff\\MichaelisMentenDemo\\'),
               a.binaries,
               a.zipfiles,
               a.datas,
			   *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
               strip=False,
               upx=True,
               name='PolyEnzyme')
