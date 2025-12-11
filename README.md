
# Cozy Cove – Game Project  
A Python/Pygame-based virtual pet simulation featuring creature management, drag‑and‑drop inventory interactions, a dynamic satisfaction system, and a modular UI framework. This project demonstrates event‑driven architecture, custom UI components, state persistence, and a multi‑scene game loop.

---

## Overview  
Virtual Creature Care is a desktop game where players manage a small ecosystem of creatures, each with unique behaviors, needs, and satisfaction levels. The player interacts with creatures through feeding, petting, and applying special effects, while navigating a fully custom UI system built on top of Pygame.

The project emphasizes clean modular design, extensible UI components, and robust event handling across multiple interactive layers.

---

## Features

### Core Gameplay  
- Multiple creature types with unique preferences and satisfaction responses  
- Real‑time satisfaction decay, modifiers, and temporary effects  
- Click‑to‑select, drag‑to‑move creatures  
- Petting mode with toggleable drag behavior  
- Game over state when all creatures reach zero satisfaction  

### Inventory & Items  
- Drag‑and‑drop feeding system  
- Click‑to‑use and SHIFT‑drag item interactions  
- Food, Potion, and Cleanse item categories  
- Dynamic quantity tracking and UI updates  
- Marketplace for purchasing items with in‑game currency  

### UI System  
Custom-built UI framework including:  
- Button, Text, InputField, InfoBox components  
- Tabbed Toolbar with multiple views (Actions, Inventory, Mini‑Game)  
- InventorySlot with drag logic and collision‑based item usage  
- BackgroundManager for scene‑specific backgrounds  
- Menu and MenuManager for pause menus and setup screens  

### Scenes & State  
- GameScene with full creature simulation  
- Setup menu for world initialization  
- Pause menu with save/load functionality  
- Persistent save system using custom serialization  

### Additional Systems  
- Soft collision resolution between creatures  
- Global satisfaction bar  
- Admin/debug panel with commands (spawn, reset, refill, master mode)  
- Mini‑game launcher (Flappy Bird variant)  

---

## Project Structure (High-Level)

```
project/
│
├── game_manager.py        # UI components, Toolbar, InventorySlot, Menus
├── gameplay .py           # Main gameplay loop and creature interactions
├── classes.py             # Creature, Items, Effects, Inventory, Money
├── persistence.py         # Save/load system
├── logger.py              # Logging system
├── minigames/             # Mini‑game modules
├── assets/                # Sprites, backgrounds, music, item icons
└── main.py                # Entry point and scene switching
```

---

## Controls

### Creature Interaction  
- Left Click: Select creature  
- Drag (when allowed): Move creature  
- Right Click: Deselect creature  
- Petting Mode: Toggle via toolbar  

### Inventory  
- Left Click: Use item on selected creature  
- SHIFT + Drag: Drag item to selected creature  
- Drop item onto selected creature to apply effects  

### UI  
- Toolbar Tabs: Switch between Actions, Inventory, Mini‑Game  
- Hamburger Button: Pause menu  
- Admin Mode: Press `/` to toggle  

---

## Installation & Running

### Requirements  
- Python 3.10+  
- Pygame  

### Install dependencies  
```
pip install pygame
```

### Run the game  
```
python main.py
```

---

## Saving & Loading  
The game automatically saves world state (creatures, inventory, money, satisfaction totals) using the Persistence module. Save files are stored per world name and can be reloaded from the main menu.

---

## Design Notes  
This project was built with a focus on:  
- Modular UI architecture  
- Clear separation between game logic and rendering  
- Robust event propagation across UI layers  
- Extensible systems for future features (more items, more tabs, more creatures)  
- Maintainable code structure suitable for long‑term iteration  

---
