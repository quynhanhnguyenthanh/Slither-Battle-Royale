[app]

# Tên hiển thị của ứng dụng
title = Slither Sinh Ton

# Tên gói (không dấu, không khoảng trắng)
package.name = slithersurvival
package.domain = org.oop.slither

# Thư mục nguồn chứa main.py
source.dir = .

# Các loại file được đóng gói vào APK
source.include_exts = py,png,jpg,jpeg,kv,atlas,wav,mp3,ogg,json,ttf

# Phiên bản ứng dụng
version = 1.0

# Thư viện phụ thuộc
requirements = python3,kivy,av,numpy

# Hướng màn hình: dọc (portrait) cho game điện thoại
orientation = portrait

# Toàn màn hình (0 = có thanh trạng thái)
fullscreen = 0

# Icon và màn hình khởi động (bỏ comment nếu có file)
# icon.filename = %(source.dir)s/assets/images/icon.png
# presplash.filename = %(source.dir)s/assets/images/presplash.png

[buildozer]

# Mức log (2 = chi tiết)
log_level = 2
warn_on_root = 1

[app:android]

# API và kiến trúc
android.api = 33
android.minapi = 21
android.archs = arm64-v8a, armeabi-v7a

# Quyền (game này không cần quyền đặc biệt)
android.permissions =

# Cho phép sao lưu dữ liệu (data.json)
android.allow_backup = True

