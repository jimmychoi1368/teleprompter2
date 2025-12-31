[app]
# 基础配置
title = EnglishTeleprompter
package.name = teleprompter
package.domain = org.teleprompter
version = 1.0.0
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,zip,aar

# Python版本
python.version = 3.10

# 安卓架构（适配主流手机）
android.archs = arm64-v8a, armeabi-v7a

# 权限（语音识别+文件读写）
android.permissions = RECORD_AUDIO, INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# Vosk资源路径（匹配0.3.70版本AAR）
android.add_aars = libs/vosk-android-0.3.70.aar
android.add_jars = libs/vosk-android-0.3.70.aar
android.add_assets = assets/

# 依赖（稳定版本组合）
requirements = python3,kivy==2.2.1,pyjnius==1.5.0,setuptools

# 安卓版本（适配Buildozer 1.5.0）
android.api = 31
android.ndk = 23b
android.build_tools = 33.0.2
android.disable_update_check = True

[buildozer]
# 最详细日志（便于排查）
log_level = 3
warn_on_root = 1
buildozer.version = 1.5.0
