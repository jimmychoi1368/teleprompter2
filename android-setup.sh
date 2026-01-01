#!/bin/bash
set -e

echo "设置Android SDK..."

# 使用sudo更新和安装包
sudo apt-get update
sudo apt-get install -y wget unzip openjdk-11-jdk

# 下载Android命令行工具
wget -q https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip
unzip -q commandlinetools-linux-9477386_latest.zip
rm commandlinetools-linux-9477386_latest.zip

# 创建正确的目录结构
mkdir -p android-sdk/cmdline-tools/latest
mv cmdline-tools/* android-sdk/cmdline-tools/latest/
rmdir cmdline-tools

export ANDROID_SDK_ROOT=$(pwd)/android-sdk
export ANDROID_HOME=$ANDROID_SDK_ROOT
export PATH=$PATH:$ANDROID_SDK_ROOT/cmdline-tools/latest/bin

# 创建许可证目录并写入许可证
mkdir -p $ANDROID_SDK_ROOT/licenses
echo "8933bad161af4178b1185d1a37fbf41ea5269c55" > $ANDROID_SDK_ROOT/licenses/android-sdk-license
echo "84831b9409646a918e30573b4d6d4f0c7d11e53a" >> $ANDROID_SDK_ROOT/licenses/android-sdk-license
echo "d56f5187479451eabf01fb78af6dfcb131a6481e" >> $ANDROID_SDK_ROOT/licenses/android-sdk-license

# 安装Android组件
$ANDROID_SDK_ROOT/cmdline-tools/latest/bin/sdkmanager --sdk_root=$ANDROID_SDK_ROOT "platform-tools"
$ANDROID_SDK_ROOT/cmdline-tools/latest/bin/sdkmanager --sdk_root=$ANDROID_SDK_ROOT "platforms;android-31"
$ANDROID_SDK_ROOT/cmdline-tools/latest/bin/sdkmanager --sdk_root=$ANDROID_SDK_ROOT "build-tools;33.0.2"
$ANDROID_SDK_ROOT/cmdline-tools/latest/bin/sdkmanager --sdk_root=$ANDROID_SDK_ROOT "ndk;23.1.7779620"

echo "Android SDK设置完成"
