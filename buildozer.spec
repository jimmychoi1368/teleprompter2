[app]
title = Teleprompter
package.name = teleprompter
package.domain = org.voiceprompter
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,txt,aar
source.include_patterns = assets/*,assets/vosk_model/*,libs/*
source.exclude_dirs = tests,bin,.github,.buildozer,__pycache__
source.exclude_patterns = *.pyc,*.pyo

version = 1.0.0
requirements = python3,kivy==2.2.1,pyjnius==1.5.0,android

presplash.filename = %(source.dir)s/presplash.png
icon.filename = %(source.dir)s/icon.png

orientation = landscape
fullscreen = 1

android.permissions = RECORD_AUDIO,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,BLUETOOTH,BLUETOOTH_ADMIN,BLUETOOTH_CONNECT,INTERNET,ACCESS_NETWORK_STATE

android.api = 33
android.minapi = 24
android.sdk = 33
android.ndk = 25b
android.ndk_api = 24

android.archs = arm64-v8a,armeabi-v7a

android.allow_backup = True
android.accept_sdk_license = True

android.add_aars = libs/vosk-android-1.3.0.aar

android.enable_androidx = True

p4a.branch = master
p4a.bootstrap = sdl2

[buildozer]
log_level = 2
warn_on_root = 1
