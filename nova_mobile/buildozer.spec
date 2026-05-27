[app]
title = NOVA Mobile
icon.filename = logo.png
package.name = novamobile
package.domain = org.shreyans
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,env
version = 1.0.0
requirements = python3,kivy==2.3.0,kivymd==1.2.0,httpx,certifi,idna,sniffio,anyio,python-dotenv
orientation = portrait
fullscreen = 1
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True
android.permissions = INTERNET

[buildozer]
log_level = 2