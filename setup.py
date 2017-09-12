#!/usr/bin/env python3

# python setup.py sdist --format=zip,gztar

from setuptools import setup
import os
import sys
import platform
import imp
import argparse

version = imp.load_source('version', 'lib/version.py')

if sys.version_info[:3] < (3, 4, 0):
    sys.exit("Error: Electrum requires Python version >= 3.4.0...")

data_files = []

if platform.system() in ['Linux', 'FreeBSD', 'DragonFly']:
    parser = argparse.ArgumentParser()
    parser.add_argument('--root=', dest='root_path', metavar='dir', default='/')
    opts, _ = parser.parse_known_args(sys.argv[1:])
    usr_share = os.path.join(sys.prefix, "share")
    if not os.access(opts.root_path + usr_share, os.W_OK) and \
       not os.access(opts.root_path, os.W_OK):
        if 'XDG_DATA_HOME' in os.environ.keys():
            usr_share = os.environ['XDG_DATA_HOME']
        else:
            usr_share = os.path.expanduser('~/.local/share')
    data_files += [
        (os.path.join(usr_share, 'applications/'), ['electrum-zeny.desktop']),
        (os.path.join(usr_share, 'pixmaps/'), ['icons/electrum.png'])
    ]

setup(
    name="Electrum-ZENY",
    version=version.ELECTRUM_VERSION,
    install_requires=[
        'pyaes>=0.1a1',
        'ecdsa>=0.9',
        'pbkdf2',
        'requests',
        'qrcode',
        'zny_yescrypt',
        'protobuf',
        'dnspython',
        'jsonrpclib-pelix',
        'PySocks>=1.6.6',
    ],
    packages=[
        'electrum_zeny',
        'electrum_zeny_gui',
        'electrum_zeny_gui.qt',
        'electrum_zeny_plugins',
        'electrum_zeny_plugins.audio_modem',
        'electrum_zeny_plugins.cosigner_pool',
        'electrum_zeny_plugins.email_requests',
        'electrum_zeny_plugins.greenaddress_instant',
        'electrum_zeny_plugins.hw_wallet',
        'electrum_zeny_plugins.keepkey',
        'electrum_zeny_plugins.labels',
        'electrum_zeny_plugins.ledger',
        'electrum_zeny_plugins.trezor',
        'electrum_zeny_plugins.digitalbitbox',
        'electrum_zeny_plugins.virtualkeyboard',
    ],
    package_dir={
        'electrum_zeny': 'lib',
        'electrum_zeny_gui': 'gui',
        'electrum_zeny_plugins': 'plugins',
    },
    package_data={
        'electrum_zeny': [
            'currencies.json',
            'www/index.html',
            'wordlist/*.txt',
            'locale/*/LC_MESSAGES/electrum.mo',
        ]
    },
    scripts=['electrum-zeny'],
    data_files=data_files,
    description="Lightweight Bitzeny Wallet",
    author="Thomas Voegtlin",
    author_email="thomasv@electrum.org",
    license="MIT Licence",
    url="https://github.com/wakiyamap/electrum-zeny",
    long_description="""Lightweight Bitzeny Wallet"""
)
