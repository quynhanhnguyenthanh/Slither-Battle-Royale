# 🐍 Slither Sinh Tồn — Slither Battle Royale (Đồ án OOP · Kivy)

Game sinh tồn kiểu **slither.io**: chuyển động **liên tục 360°** bám theo con trỏ,
ăn mồi để dài ra, tăng tốc để né/rượt, hạ hết bot để **CHIẾN THẮNG**.
Đâm vào thân rắn khác hoặc mép sân = **THUA**. Dùng sprite/âm thanh thật trong `assets/`.

## ▶️ Chạy
```bash
pip install -r requirements.txt
python main.py
```

## 🎮 Điều khiển
- **Xoay 360°:** di chuột — rắn luôn bẻ lái mượt về phía con trỏ (trên điện thoại: kéo ngón tay).
- **Tăng tốc:** giữ **chuột trái** hoặc **phím Space** (hoặc giữ nút **BOOST** góc phải, tiện cảm ứng).
  Khi tăng tốc rắn **ngắn dần** và có **vệt sáng ở đuôi**.
- **Tạm dừng:** nút **II** ở góc trên.

## ✅ Các tính năng 
| Yêu cầu | Cài đặt trong code |
|---|---|
| Di chuyển mượt 360° bám con trỏ (như slither.io) | `BaseSnake._turn_toward` + `TURN_RATE`, lái theo `Window.mouse_pos` trong `GameWidget.update` |
| Tăng tốc khi giữ chuột trái/Space, trừ dần độ dài | `BOOST_SPEED`, `BOOST_DRAIN`, nguồn boost trong `GameWidget` |
| Bot tự tìm mồi + bẻ lái né va chạm | `BotSnake.update_direction` (tìm mồi gần nhất + quét góc né bằng `point_blocked`) |
| Ăn mồi → dài ra, to hơn, cộng điểm | `grow()`, bán kính `snake_radius(length)`, `score` |
| Chết khi đầu chạm thân người khác hoặc mép sân | `GameWidget._collides` (sân tròn `ARENA_RADIUS`) |
| Xác kẻ thua biến thành dải mồi lớn | `GameWidget._drop_loot` sinh `Loot` dọc thân |
| Lưu tự động điểm cao/coin/skin | `DataManager.save()` khi kết thúc ván, mua skin, đổi cài đặt, và khi thoát |
| Cửa hàng mua/đổi skin bằng coin | `ShopScreen` |
| Âm thanh (nhạc nền, ăn mồi) + hiệu ứng (vệt sáng) + bật/tắt ở Cài đặt | `AudioManager`, vệt sáng `blur.png` khi boost, `SettingsScreen` (bật/tắt hiệu ứng & nhạc) |

## 📁 Cấu trúc
```
main.py                # Khởi chạy + ScreenManager
config.py              # Hằng số vật lý + bảng skin
utils/  data_manager.py  audio.py  assets.py  game_data.json
entities/  snake.py (BaseSnake→PlayerSnake/BotSnake)  collectibles.py (Food→Loot)
screens/  main_menu  game_screen  shop_screen  settings_screen  result_screens
assets/  images/skins  images/ui  sounds
```

## 🎯 Bản đồ OOP 
- **Đóng gói:** `DataManager` giấu `_data`, truy cập qua get/set an toàn (tự lưu file).
- **Kế thừa:** `PlayerSnake`/`BotSnake` ← `BaseSnake`; `Loot` ← `Food`; các màn ← `Screen`.
- **Đa hình:** `update_direction()` — Player lái theo con trỏ, Bot lái theo AI, gọi chung một tên.
- **Trừu tượng:** `BaseSnake` lo vật lý chung (quay, tiến, bám thân, dài/ngắn); lớp con chỉ lo cách chọn hướng.

## 🧠 Thuật toán
- **Chuyển động 360°:** đầu tiến đều theo `angle`; mỗi khung, `angle` quay dần về `target_angle` (góc từ đầu tới con trỏ) tối đa `TURN_RATE`·dt → mượt như slither.io.
- **Thân:** chuỗi điểm, mỗi đốt luôn cách đốt trước `SEG_SPACING` (bám đuôi liền mạch).
- **Bot AI:** chọn mồi gần nhất; nếu hướng đó bị chặn (mép sân/thân rắn) thì quét các góc lệch để tìm hướng thoáng gần nhất.
- **Va chạm:** đầu ra ngoài bán kính sân, hoặc đầu chạm gần điểm thân của rắn khác → chết.
- **Camera:** bám đầu người chơi, tự thu nhỏ (`snake_zoom`) khi rắn dài để vẫn bao quát.

## 📦 Đóng gói APK (Linux/macOS/WSL)
```bash
pip install buildozer cython
buildozer -v android debug   # file .apk nằm trong bin/
```
