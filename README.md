# 🐍 Slither Sinh Tồn — Slither Battle Royale (Đồ án OOP · Kivy)

Game rắn sinh tồn kiểu *slither.io* trên lưới, dùng **sprite thật** trong `assets/`.
Người chơi ăn mồi để dài ra và ghi điểm, né các rắn máy (bot).
**Hạ hết bot để CHIẾN THẮNG**; đâm tường / thân rắn khác là THUA.

## ▶️ Chạy

```bash
pip install -r requirements.txt
python main.py
```

Điều khiển: **điện thoại** chạm/kéo về hướng muốn đi · **máy tính** phím mũi tên hoặc `W A S D`.

Đóng gói Android (Linux/WSL/macOS):
```bash
pip install buildozer cython
buildozer -v android debug
```

## 📁 Cấu trúc (khớp repo)

```
├── main.py                  # Khởi chạy + ScreenManager
├── config.py                # Hằng số + bảng skin (map tới sprite)
├── buildozer.spec
├── utils/
│   ├── data_manager.py      # DataManager        (Đóng gói)
│   ├── audio.py             # AudioManager        (map sự kiện -> .ogg)
│   ├── assets.py            # Nạp/cache texture, đường dẫn ảnh UI
│   └── game_data.json       # File lưu mẫu (runtime lưu ở user_data_dir)
├── entities/
│   ├── snake.py             # BaseSnake → PlayerSnake, BotSnake  (Kế thừa, Đa hình)
│   └── collectibles.py      # Food → Loot
├── screens/
│   ├── main_menu.py         # Menu (backdrop + logo + vignette)
│   ├── settings_screen.py   # Âm lượng, bật/tắt hiệu ứng
│   ├── shop_screen.py       # Cửa hàng skin (preview sprite thật)
│   ├── game_screen.py       # GameWidget + GameScreen (gameplay, va chạm, camera)
│   └── result_screens.py    # GameOver + GameWin
└── assets/                  # skins, ui, sounds (đã có sẵn trong repo)
```

## 🎨 Cách dùng assets

- **Skin** (`assets/images/skins`): mỗi đốt rắn là 1 sprite tròn 512×512 vẽ gối lên nhau;
  đầu dùng sprite `*_head` (awesome/stare/vamp) hoặc dùng ảnh thân + ghép 2 mắt
  (`snake_eye_left/right`). Đầu tự **xoay theo hướng đi**.
- **UI** (`assets/images/ui`): `menu_title` (logo), `backdrop` (nền), `vignette`
  (viền tối), `circle` (vẽ mồi), `skin_indicator` / `skin_indicator_locked`
  (trạng thái sở hữu trong shop).
- **Âm thanh** (`assets/sounds`, .ogg) — ánh xạ trong `utils/audio.py`:
  ăn mồi→`alert_money`, chết→`error_2`, thắng→`start_game`, bấm nút→`button_up`,
  chuyển màn→`navigate`, hạ bot→`whoosh`.

## 🎯 Bản đồ OOP (cho báo cáo Chương 3)

| Khái niệm | Thể hiện trong code |
|---|---|
| **Đóng gói** | `DataManager` giấu `_data`, chỉ truy cập qua get/set an toàn |
| **Kế thừa** | `PlayerSnake`/`BotSnake` ← `BaseSnake`; `Loot` ← `Food`; các màn hình ← `Screen` |
| **Đa hình** | `update_direction()` ghi đè khác nhau ở Player (input) và Bot (AI); gọi chung một tên |
| **Trừu tượng** | `BaseSnake` định nghĩa `move/die/grow` chung; lớp con chỉ lo phần khác biệt |
| **Tương tác đối tượng** | `GameWidget` điều phối `Snake` ↔ `Food/Loot` ↔ va chạm ↔ HUD |

## 🧠 Thuật toán chính
- **Di chuyển:** thân là danh sách ô (đầu ở đầu list); mỗi bước chèn đầu mới, bỏ đuôi (giữ đuôi khi ăn mồi).
- **AI Bot:** tìm mồi gần nhất (khoảng cách Manhattan), chọn hướng an toàn (không đâm tường/thân) để tiến lại gần, kèm chút ngẫu nhiên.
- **Va chạm:** ra biên → chết; đầu trùng thân bất kỳ (kể cả chính nó) → chết; hai đầu cùng ô → cả hai chết.
- **Camera:** luôn đặt đầu người chơi ở tâm; thế giới cuộn quanh.
- **Loot:** rắn chết rớt mồi lớn dọc thân.

