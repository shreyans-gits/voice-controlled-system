[app]
title = NOVA Desktop Link
package.name = novadesktoplink
package.domain = org.shreyans
icon.filename = logo.png
presplash.filename = logo.png

source.dir = .
source.include_exts = py,png,jpg,kv,txt,json,ini

version = 1.0.0

# No python3 version pin — let p4a own the Python version
requirements = python3,kivy==2.2.1,kivymd==1.2.0,httpx,certifi,idna,sniffio,anyio,python-dotenv,numpy,pillow,requests,plyer

orientation = portrait
fullscreen = 1

android.permissions = INTERNET, CAMERA, RECORD_AUDIO, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

android.api = 33
android.minapi = 24
android.ndk = 25b
android.ndk_api = 24
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True
android.accept_sdk_license = True

p4a.branch = v2024.01.21
p4a.commit = 7df5ac3

android.release_artifact = apk

[buildozer]
log_level = 2
warn_on_root = 1