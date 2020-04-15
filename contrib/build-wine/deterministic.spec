# -*- mode: python -*-

from PyInstaller.utils.hooks import collect_data_files, collect_submodules, collect_dynamic_libs

import sys
import os
for i, x in enumerate(sys.argv):
    if x == '--name':
        cmdline_name = sys.argv[i+1]
        break
else:
    raise Exception('no name')

PYHOME = 'c:/python3'

home = 'C:\\electrum-mona\\'

if os.path.exists("C:/Program Files (x86)"):
    zbardir = 'C:\\Program Files (x86)\\'
else:
    zbardir = 'C:\\Program Files\\'

# see https://github.com/pyinstaller/pyinstaller/issues/2005
hiddenimports = []
hiddenimports += collect_submodules('trezorlib')
hiddenimports += collect_submodules('safetlib')
hiddenimports += collect_submodules('btchip')
hiddenimports += collect_submodules('keepkeylib')
hiddenimports += collect_submodules('websocket')
hiddenimports += collect_submodules('ckcc')
hiddenimports += ['PyQt5.QtPrintSupport']  # needed by Revealer


binaries = []

# Workaround for "Retro Look":
binaries += [b for b in collect_dynamic_libs('PyQt5') if 'qwindowsvista' in b[0]]

binaries += [('C:/tmp/libsecp256k1-0.dll', '.')]
binaries += [('C:/tmp/libusb-1.0.dll', '.')]

datas = [
    (home+'electrum_mona/*.json', 'electrum_mona'),
    (home+'electrum_mona/lnwire/*.csv', 'electrum_mona/lnwire'),
    (home+'electrum_mona/wordlist/english.txt', 'electrum_mona/wordlist'),
    (home+'electrum_mona/locale', 'electrum_mona/locale'),
    (home+'electrum_mona/plugins', 'electrum_mona/plugins'),
    (zbardir+'ZBar\\bin\\', '.'),
    (home+'electrum_mona/gui/icons', 'electrum_mona/gui/icons'),
]
datas += collect_data_files('trezorlib')
datas += collect_data_files('safetlib')
datas += collect_data_files('btchip')
datas += collect_data_files('keepkeylib')
datas += collect_data_files('ckcc')
datas += collect_data_files('jsonrpcserver')
datas += collect_data_files('jsonrpcclient')

# We don't put these files in to actually include them in the script but to make the Analysis method scan them for imports
a = Analysis([home+'run_electrum',
              home+'electrum_mona/gui/qt/main_window.py',
              home+'electrum_mona/gui/text.py',
              home+'electrum_mona/util.py',
              home+'electrum_mona/wallet.py',
              home+'electrum_mona/simple_config.py',
              home+'electrum_mona/bitcoin.py',
              home+'electrum_mona/dnssec.py',
              home+'electrum_mona/commands.py',
              home+'electrum_mona/plugins/cosigner_pool/qt.py',
              home+'electrum_mona/plugins/email_requests/qt.py',
              home+'electrum_mona/plugins/trezor/qt.py',
              home+'electrum_mona/plugins/safe_t/client.py',
              home+'electrum_mona/plugins/safe_t/qt.py',
              home+'electrum_mona/plugins/keepkey/qt.py',
              home+'electrum_mona/plugins/ledger/qt.py',
              home+'electrum_mona/plugins/coldcard/qt.py',
              #home+'packages/requests/utils.py'
              ],
             binaries=binaries,
             datas=datas,
             #pathex=[home+'lib', home+'gui', home+'plugins'],
             hiddenimports=hiddenimports,
             hookspath=[])


# http://stackoverflow.com/questions/19055089/pyinstaller-onefile-warning-pyconfig-h-when-importing-scipy-or-scipy-signal
for d in a.datas:
    if 'pyconfig' in d[0]:
        a.datas.remove(d)
        break

# Strip out parts of Qt that we never use. Reduces binary size by tens of MBs. see #4815
qt_bins2remove=('qt5web', 'qt53d', 'qt5game', 'qt5designer', 'qt5quick',
                'qt5location', 'qt5test', 'qt5xml', r'pyqt5\qt\qml\qtquick')
print("Removing Qt binaries:", *qt_bins2remove)
for x in a.binaries.copy():
    for r in qt_bins2remove:
        if x[0].lower().startswith(r):
            a.binaries.remove(x)
            print('----> Removed x =', x)

qt_data2remove=(r'pyqt5\qt\translations\qtwebengine_locales', )
print("Removing Qt datas:", *qt_data2remove)
for x in a.datas.copy():
    for r in qt_data2remove:
        if x[0].lower().startswith(r):
            a.datas.remove(x)
            print('----> Removed x =', x)

# hotfix for #3171 (pre-Win10 binaries)
a.binaries = [x for x in a.binaries if not x[1].lower().startswith(r'c:\windows')]

pyz = PYZ(a.pure)


#####
# "standalone" exe with all dependencies packed into it

exe_standalone = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    name=os.path.join('build\\pyi.win32\\electrum-mona', cmdline_name + ".exe"),
    debug=False,
    strip=None,
    upx=False,
    icon=home+'electrum_mona/gui/icons/electrum.ico',
    console=False)
    # console=True makes an annoying black box pop up, but it does make Electrum output command line commands, with this turned off no output will be given but commands can still be used

exe_portable = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas + [ ('is_portable', 'README.md', 'DATA' ) ],
    name=os.path.join('build\\pyi.win32\\electrum-mona', cmdline_name + "-portable.exe"),
    debug=False,
    strip=None,
    upx=False,
    icon=home+'electrum_mona/gui/icons/electrum.ico',
    console=False)

#####
# exe and separate files that NSIS uses to build installer "setup" exe

exe_dependent = EXE(
    pyz,
    a.scripts,
    exclude_binaries=True,
    name=os.path.join('build\\pyi.win32\\electrum-mona', cmdline_name),
    debug=False,
    strip=None,
    upx=False,
    icon=home+'electrum_mona/gui/icons/electrum.ico',
    console=False)

coll = COLLECT(
    exe_dependent,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=None,
    upx=True,
    debug=False,
    icon=home+'electrum_mona/gui/icons/electrum.ico',
    console=False,
    name=os.path.join('dist', 'electrum-mona'))
