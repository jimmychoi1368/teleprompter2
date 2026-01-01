#!/bin/bash
set -e
echo "设置Android SDK..."
apt-get update
apt-get install -y wget unzip openjdk-11-jdk
wget -q https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip
unzip -q commandlinetools-linux-9477386_latest.zip
rm commandlinetools-linux-9477386_latest.zip
mkdir -p android-sdk/cmdline-tools/latest
mv cmdline-tools/* android-sdk/cmdline-tools/latest/
rmdir cmdline-tools
export ANDROID_SDK_ROOT=$(pwd)/android-sdk
export ANDROID_HOME=$ANDROID_SDK_ROOT
mkdir -p $ANDROID_SDK_ROOT/licenses
echo "8933bad161af4178b1185d1a37fbf41ea5269c55" > $ANDROID_SDK_ROOT/licenses/android-sdk-license
$ANDROID_SDK_ROOT/cmdline-tools/latest/bin/sdkmanager --sdk_root=$ANDROID_SDK_ROOT "platform-tools"
$ANDROID_SDK_ROOT/cmdline-tools/latest/bin/sdkmanager --sdk_root=$ANDROID_SDK_ROOT "platforms;android-31"
$ANDROID_SDK_ROOT/cmdline-tools/latest/bin/sdkmanager --sdk_root=$ANDROID_SDK_ROOT "build-tools;33.0.2"
$ANDROID_SDK_ROOT/cmdline-tools/latest/bin/sdkmanager --sdk_root=$ANDROID_SDK_ROOT "ndk;23.1.7779620"
echo "Android SDK设置完成"

