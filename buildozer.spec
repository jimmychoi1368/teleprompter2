[app]
title = EnglishTeleprompter
package.name = teleprompter
package.domain = org.teleprompter
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,zip,aar
source.include_patterns = assets/*,libs/*
source.exclude_dirs = tests,bin,.github,.buildozer,__pycache__

version = 1.0.0
requirements = python3,kivy==2.2.1,pyjnius==1.5.0

orientation = landscape
fullscreen = 1

android.permissions = RECORD_AUDIO,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,INTERNET

android.api = 33
android.minapi = 24
android.sdk = 33
android.ndk = 25b
android.ndk_api = 24
android.build_tools = 33.0.2

android.archs = arm64-v8a,armeabi-v7a

android.allow_backup = True
android.accept_sdk_license = True

android.add_aars = libs/vosk-android-1.4.0.aar
android.add_assets = assets/

android.enable_androidx = True
android.disable_update_check = True

p4a.branch = master
p4a.bootstrap = sdl2

[buildozer]
log_level = 2
warn_on_root = 1
