[app]
title = AppSpese
package.name = appspese
package.domain = org.appspese
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt
version = 1.0

requirements = python3,kivy==2.3.0,kivymd==1.1.1,requests

android.permissions = INTERNET
android.minapi = 21
android.api = 33
android.ndk = 25b
android.archs = arm64-v8a

[buildozer]
log_level = 2