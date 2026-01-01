[app]
title = EnglishTeleprompter
package.name = teleprompter
package.domain = org.teleprompter
version = 1.0.0
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,zip,aar
python.version = 3.10
android.archs = arm64-v8a, armeabi-v7a
android.permissions = RECORD_AUDIO, INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
android.add_aars = libs/vosk-android-0.3.70.aar
android.add_jars = libs/vosk-android-0.3.70.aar
android.add_assets = assets/
requirements = python3,kivy==2.2.1,pyjnius==1.5.0,setuptools
android.api = 31
android.ndk = 25b
android.build_tools = 33.0.2

[buildozer]
log_level = 2
warn_on_root = 1
build_dir = ./.buildozer
bin_dir = ./bin
allow_root = 1
