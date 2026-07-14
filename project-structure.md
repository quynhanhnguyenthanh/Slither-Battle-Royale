# Cấu trúc project Slither-Battle-Royale

```
Slither-Battle-Royale/
├── main.py                  # App class (kế thừa kivy App)
├── config.py                # Hằng số, màu, skin list, UI map
│
├── screens/
│   ├── __init__.py
│   ├── main_menu.py         # MainMenuScreen
│   ├── game_screen.py       # GameScreen + GameWidget (vòng lặp game, HUD, pause)
│   ├── result_screens.py    # ResultScreen → GameOverScreen / GameWinScreen
│   ├── settings_screen.py   # SettingsScreen (volume, sfx toggle)
│   └── shop_screen.py       # ShopScreen + SkinCard (cửa hàng skin)
│
├── entities/
│   ├── __init__.py
│   ├── snake.py             # SnakeBase → PlayerSnake, BotSnake
│   └── collectibles.py      # Food, Loot
│
└── utils/
    ├── __init__.py
    ├── assets.py            # Asset loader (texture, skin, UI images)
    ├── audio.py             # AudioManager (SoundLoader / afplay)
    └── data_manager.py      # DataManager (JSON save/load, coin, skin ownership)
```
