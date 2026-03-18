# RUST & RUIN: The Last Child
### A Post-Apocalyptic 2D Story Puzzle Adventure

---

## 🚀 HOW TO RUN

### 1. Install dependencies
```bash
pip install pygame numpy
```

### 2. Run the game
```bash
cd robot_apocalypse
python main.py
```

That's it. Fully offline, no external assets needed.

---

## 🎮 CONTROLS

| Key | Action |
|-----|--------|
| `←` / `A` | Move left |
| `→` / `D` | Move right |
| `SPACE` / `W` / `↑` | Jump |
| `E` / `ENTER` | Interact with object / Confirm puzzle |
| `X` / `Z` | Attack nearby enemy |
| `ESC` | Pause / Exit puzzle / Return to menu |
| `TAB` | Skip cutscene |

---

## 📋 GAME OVERVIEW

**Story:** You are KAI, a child survivor in a world destroyed by robots. Your companion AXIOM — a defective robot who refuses to serve The Collective — guides you across 4 devastated levels to find other survivors.

### Levels
1. **The Rusted Slums** — Broken city, neon-lit ruins
2. **Scorched Desert** — Endless sand dunes, ancient AI relics
3. **Crystalline Beach** — Coastal survival camp
4. **The Battlefield** — War zone + Boss fight

### Gameplay Loop
```
Explore → Find Puzzle Triggers → Solve Puzzles → Unlock Exit → Cutscene → Next Level
```

### Puzzles (6 types)
| Puzzle | Description |
|--------|-------------|
| Math Cipher | Solve an arithmetic equation to unlock a door |
| Tic-Tac-Toe | Beat or draw with AXIOM's minimax AI |
| Connect Four | Outmaneuver the tactical AI (minimax depth-4) |
| Pattern Lock | Memorize and repeat a color sequence |
| Missing Object | Identify the hidden shape from visual clues |
| Power Grid | Connect all nodes to the power source (BFS solver) |

### Boss Fight (Level 4)
- **Phase 1:** Slow charge + missiles
- **Phase 2:** Faster, double missiles
- **Phase 3:** The TWIST — the boss robot is piloted by a COW
- **Ending:** Alien abduction animated cutscene

### Enemies
- **Drone** — Hover-patrol, rushes player when nearby
- **Guard** — Ground patrol, simple chase
- **Turret** — Stationary, area-denial

---

## 🎬 DEVELOPER FEATURES

From the **Main Menu → CUTSCENES** you can preview all 7 cutscenes without playing:
- Intro
- Slum Complete
- Desert Complete  
- Beach Complete
- Boss Intro
- Boss Twist (Cow Reveal)
- Ending + Alien Abduction

---

## 📁 PROJECT STRUCTURE

```
robot_apocalypse/
├── main.py                    # Entry point, game loop
├── constants.py               # Global constants & colors
├── engine/
│   ├── renderer.py            # Camera, world-to-screen, draw calls
│   ├── physics.py             # Gravity, collision resolution
│   └── input.py               # Key state, just-pressed detection
├── game/
│   ├── player.py              # Player entity, input, animation
│   ├── robot_companion.py     # AXIOM AI companion, hints, dialogue
│   ├── enemy.py               # Drone/Guard/Turret enemy types
│   └── boss.py                # Multi-phase boss + cow reveal
├── systems/
│   ├── ai_system.py           # Minimax TTT+C4, rule-based enemies
│   ├── puzzle_engine.py       # All 6 puzzle implementations
│   ├── cutscene_manager.py    # All 7 cutscene scripts + alien anim
│   ├── dialogue_system.py     # Typewriter dialogue boxes
│   ├── story_engine.py        # Narrative flag system
│   └── level_manager.py       # Level loading, trigger routing
├── levels/
│   ├── base_level.py          # Platform/Interactable base classes
│   ├── slum.py                # Level 1 — Math + Tic-Tac-Toe
│   ├── desert.py              # Level 2 — Pattern + Tic-Tac-Toe
│   ├── beach.py               # Level 3 — Missing Object + Power Grid
│   └── battlefield.py         # Level 4 — Connect Four + Math + Boss
└── ui/
    ├── menu.py                # Main menu, instructions, cutscene viewer
    └── hud.py                 # Health bar, score, puzzle counter, boss HP
```

---

## 🤖 AI SYSTEMS

- **Tic-Tac-Toe:** Full minimax with alpha-beta pruning (unbeatable)
- **Connect Four:** Minimax depth-4 with heuristic board scoring
- **Enemy movement:** Rule-based state machine (patrol / alert / chase)
- **Boss:** 3-phase scripted behavior with increasing speed and missiles
- **AXIOM companion:** Context-aware hint rotation per level

---

## ⚙️ TECHNICAL NOTES

- Pure Python + Pygame (no external assets)
- All graphics drawn procedurally with Pygame primitives
- Runs at 60 FPS, gravity simulation at 1200 px/s²
- Parallax scrolling background per level theme
- Physics: AABB collision with sub-step resolution
- BFS propagation for power grid puzzle
