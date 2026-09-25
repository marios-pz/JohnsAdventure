# John's Adventure: Chapter 1 (Godot 4 rework)

A top-down action RPG. John wakes up from a nightmare, trains with his mentor
Manos, and ends up fighting through shadow creatures and goblin caves after his
sister Cynthia is kidnapped.

This is a ground-up **rework of the original pygame game** (`../JohnsAdventure`).
The art, music and story come from the original. The code, level design and
game systems are new and built the Godot way: levels are scenes, content is
data, and gameplay code is small scripts.

- Engine: **Godot 4.7** (GDScript, Compatibility renderer, 1280×720, pixel-art filtering)
- Length: one chapter, roughly 20–30 minutes

---

## Running

1. Open `Rework/project.godot` in Godot 4.7 or newer.
2. Press **F5**. The game starts on the title screen (`ui/main_menu.tscn`).

_Continue_ resumes the autosave. The save is `user://save.json`
(_Project → Open User Data Folder_), and deleting it gives you a fresh start. Level
scenes can be opened and edited in the editor, but they are played through
`main.tscn`, which adds John, the HUD and the save/quest state.

### Controls

Keyboard/mouse and controller both work at any time, and on-screen prompts
switch to the device you last touched. The pause menu has a **How to Play**
card with the full list.

| Action                               | Keyboard & mouse | Controller (Xbox layout)             |
| ------------------------------------ | ---------------- | ------------------------------------ |
| Move                                 | W A S D          | Left stick                           |
| Aim                                  | Mouse            | Right stick (else: facing direction) |
| Attack (3-hit combo)                 | Left click       | X / RT                               |
| Dash (invulnerable, cancels attacks) | C                | RB                                   |
| Parry (blocks a strike, stuns)       | Shift            | LB                                   |
| Talk / open / use                    | Space            | A                                    |
| Drink potion                         | Q                | D-pad up                             |
| Inventory, stats, quest log          | E                | Y                                    |
| Back / close                         | Esc              | B                                    |
| Pause                                | Esc or P         | Menu                                 |
| Fullscreen                           | F11              | -                                    |

Controls are fixed on purpose (no rebinding). To change a default, edit
_Project → Project Settings → Input Map_.

### Tutorial

New players get a guided tutorial: one tip at a time (top right), ticked off
when they actually do it. The tips cover moving, interacting, getting a sword,
attacking, the combo, the inventory, dashing and potions. Tips live in
`data/tutorial.json` and are tied to levels and quest steps. Gameplay reports
actions with `Tutorial.notify("dash")`, etc.

### Screen sizes

The stretch aspect is `expand`. Wider screens (21:9, 32:9) show more of the
world instead of adding black bars, and every HUD/menu element is anchored to
an edge or the centre. Small rooms stay centred on very wide screens.

### Web build

The project is web-ready. It uses the Compatibility renderer, is single-threaded,
and saves to the browser's storage.

1. Install the Godot 4.7 export templates (_Editor → Manage Export Templates_).
2. Export the **Web** preset (_Project → Export_), or from a terminal:
   `godot --headless --export-release "Web" build/web/index.html`
3. Upload the contents of `build/web/` to any static host (itch.io: zip
   the folder and upload it as an HTML game). Threads are off, so no special headers are needed.

Keep `data/*.json` in the preset's **include filter**. Godot only exports resources
by default, and the story data is plain JSON read at runtime. In the browser the
Quit button is hidden, and **P** pauses too (browsers use Esc to leave fullscreen).

---

## Game design

### Core loop

Explore → talk → fight → loot chests → level up → spend upgrade points.

### Combat

- **3-hit combo.** Clicks are buffered, so the next swing starts as soon as
  the current one ends. The 3rd hit is a finisher that knocks enemies back further.
- **Crits.** The chance is John's crit stat plus the weapon's; a crit deals ×1.5.
- **Dash.** 0.18 s of invulnerability that passes through enemies, with a 0.5 s cooldown.
  It **cancels an attack** at any point without breaking the combo, and attacking
  mid-dash ends it early with a lunge into the swing. The camera zooms out, leans into the dash,
  and John leaves afterimages.
- **Parry.** John glows white for 0.22 s; a strike landing in that window is
  blocked with a spark burst and stuns the enemy (heavy ones aren't pushed back).
  A successful parry resets its 0.45 s cooldown, and parrying cancels an attack.
  A parry that catches nothing leaves John greyed out until he can parry again,
  and pressing too early says "Too soon", so mashing it is visibly punished.
- **Enemies aim.** A strike's hitbox points at John when the windup starts, in
  any direction (no safe spot under the boss), and stays there, so it can be dodged.
- **Readable enemies.** Every enemy flashes red during a wind-up before it
  strikes (the telegraph). Knockable enemies are **staggered** out of their
  wind-up when you hit them, so aggression is rewarded; heavy enemies (Guardian, boss) can't be staggered.
- **Hit feedback.** Brief hit-stop, camera shake, damage numbers (yellow = crit, purple = bleed).
- Getting hit gives John 0.6 s of invulnerability, so hits never stack unfairly.

### Progression

- XP to next level = `100 × level`. A level-up fully heals and gives **1 upgrade point**.
- Upgrades: **Damage** +2, **Endurance** +1 (a flat reduction to every hit taken), **Crit** +2 %.
- Weapons: **Training Sword** (training field chest) and **Knight Sword**. The
  Knight Sword makes enemies bleed and is found in the Cave Depths as a power
  spike right before the boss.
- Potions heal 40. They're found in chests.

### Enemies

| Enemy                     | Role                                                                           |
| ------------------------- | ------------------------------------------------------------------------------ |
| Training Dummy            | Static target that teaches the combo                                           |
| Shadow                    | Chaser with a purple aura                                                      |
| Goblin                    | Fast and fragile; comes in groups                                              |
| Guardian                  | Slow and tanky with a long spear reach and a big telegraph; can't be staggered |
| **The Big Dummie** (boss) | At half health it roars, summons 3 Shadows and gets faster                     |

### World and story flow

```
John's Room ─ Kitchen ─ Village (hub) ─┬─ Training Field
                          │    │       └─ School ──(hidden ladder)──┐
                          │    └─ Manos's Hut                       │
                          │                                         ▼
                          └──(cave mouth, opens after boss)── Cave Garden ◀─ Cave Depths ◀─ Cave Passage
```

The main quest has 11 sequential steps (`data/quests.json`). The world reacts
as it advances: Cynthia leaves the kitchen, Shadows ambush the training field,
a shadow barrier seals the school gate, the ladder is revealed, the boss
arena locks behind you, and the cave mouth opens back into the village. The
ending cutscene in Manos's hut rolls the credits.

The HUD always shows the current **objective**. Quest steps pop up as toasts,
and there is an autosave (and death checkpoint) at every level transition.

### What changed from the pygame version

- Hand-designed levels, not layout code. The world is now 9 compact
  levels; the original had 19 (9 near-identical cave rooms).
- NPC dialogue changes with story progress (`data/dialogue.json`), with multiple pages.
- Enemy attacks are telegraphed and can be staggered. The dash has i-frames, and a boss phase was added.
- Endurance and crit chance really affect combat. Diagonal movement is
  normalized, and the XP curve grows with level.
- Saves go to `user://` instead of overwriting files inside the game folder.
  One autosave format covers stats, inventory, quests, chests and cutscenes.
- Chests remember that they were opened (no infinite loot).

---

## Architecture

```
Rework/
├── project.godot        input map, autoloads, display/render settings
├── main.tscn / main.gd  gameplay root: swaps levels, spawns John, fades, death → respawn
├── autoload/            global singletons (always loaded)
│   ├── game.gd          "Game": stats, inventory, save/load, input prompts, UI event bus
│   ├── tutorial.gd      "Tutorial": guided tips completed by doing the action
│   ├── quests.gd        "Quests": sequential quest steps (reach / interact / kill)
│   └── audio.gd         "Audio": music + sound effects by name
├── data/                content as JSON (edit these to change the story)
│   ├── quests.json      quest steps
│   ├── cutscenes.json   camera/text cutscenes and what triggers them
│   ├── tutorial.json    tutorial tips
│   └── dialogue.json    NPC lines, unlocked by quest steps
├── player/              John (player.tscn + player.gd)
├── enemies/             enemy.gd (generic AI), boss.gd, one .tscn per enemy type
├── npcs/                npc.gd + one .tscn per character
├── objects/             chest, torch, exit (level transition)
├── items/               weapon.gd (Resource) + one .tres per weapon
├── props/               one .tscn per decoration (trees, houses, hills, cave walls, roads…)
├── levels/              level.gd + one .tscn per level
├── ui/                  HUD, title screen, cutscene player, credits, theme, floating text
├── assets/              sprites, sounds, fonts (converted from the pygame game)
└── tests/smoke_test.gd  headless data/wiring/quest-line check
```

### Who talks to whom

```
            ┌───────────── signals ─────────────┐
            ▼                                   │
 HUD ◀── Game (state + events) ◀── Player / NPC / Chest / Exit / Enemy
            │  travel_requested                 │
            ▼                                   ▼
          Main ──loads──▶ Level ◀── Quests.step_completed (quest gates, cutscenes)
                                    ▲
                        Cutscene ───┘ (autoload, drives the camera)
```

- **State lives in autoloads, scenes are disposable.** Levels and John are
  re-created on every transition; anything that must persist goes in `Game`
  or `Quests` and is saved.
- **Gameplay emits and UI listens.** Gameplay code never references the HUD. It
  calls `Game.open_dialogue()` and `Game.travel()`, and `Game.focus_changed` is
  emitted for the HUD to react to.
- **Interaction protocol.** Anything with an `interact()` method (on the node
  or its parent) that overlaps John's `Interactor` area on the _interactables_
  physics layer can be used. Optional methods: `can_interact()` and
  `set_highlight(on)`. It also needs a `display_name` property.

### Level scenes

Every level is a `Node2D` with `levels/level.gd` and this layout:

| Node                          | Purpose                                                                    |
| ----------------------------- | -------------------------------------------------------------------------- |
| `CanvasModulate` _(optional)_ | Present = dark level: lights are on and tint the scene. Absent = daylight. |
| `Ground`                      | Flat decoration drawn under everything (roads, grass, room background)     |
| `World`                       | **Y-sorted**: props, walls, NPCs, enemies, chests. John is added here.     |
| `Overlay`                     | Drawn on top (the black "void" around cave rooms)                          |
| `Exits`                       | `Exit` areas; `target` = level id or `credits`                             |
| `Spawns`                      | `Marker2D` per entrance, **named after the level John comes from**         |

Inspector exports on the root: `level_id`, `title`, `music`, `background`
(clear colour), `camera_limits`, `start_position`.

**Quest gates.** Add the metadata `show_after` and/or `hide_after` (a quest
step name) to _any_ node in a level. The node only exists while `show_after`
is done and `hide_after` is not, and it appears or disappears live as the story
advances. Revealed enemies play a summon effect. This single mechanism
handles every story change in the world; there is no per-level script.

### Physics layers

| Layer             | Used by                                                 |
| ----------------- | ------------------------------------------------------- |
| 1 `world`         | walls, props, NPC bodies, chests                        |
| 2 `player`        | John's body (enemy attacks and walk-in exits detect it) |
| 3 `enemies`       | enemy bodies (John's sword area detects them)           |
| 4 `interactables` | NPC/chest interact areas, doors with a prompt           |

---

## How to add content

- **A level.** Duplicate a level scene, set `level_id` (it must match the file
  name), then add `Exits` and `Spawns` both ways. Run the smoke test: it
  checks every exit has a matching spawn on the other side.
- **An enemy.** Duplicate `enemies/goblin.tscn`, swap the `SpriteFrames` (the
  animations are `idle`, `walk`, `attack`, optional `hit`, each optionally
  suffixed with `_left` or `_right`), and tune the exported stats (`speed`,
  `damage`, `attack_range`, `windup`, `recover`…). Set `kind` if a quest
  should count it.
- **An NPC.** Duplicate an `npcs/*.tscn` and give it a new `id`, then add its
  lines to `data/dialogue.json`.
- **A quest step.** Add it to `data/quests.json` (`reach` / `interact` /
  `kill`). Use its name in `show_after` / `hide_after` metadata, cutscene
  `after_step` or dialogue `after`.
- **A cutscene.** Add an entry to `data/cutscenes.json`; the step format is
  documented in its `_doc` key. It plays once when John is in `level` and
  `after_step` is done. `then` travels to a level (or the credits) when it ends.
- **A weapon.** Create a new `Weapon` resource in `items/`, set its
  `attack_frames`, and add it to `Game.WEAPONS`.

---

## Testing

```
godot --headless --path . -s tests/smoke_test.gd
```

The exit code is the number of failures. It checks that every level loads and
that every exit leads to a level which has a spawn back. It checks that no spawn
sits inside a walk-in exit (which would bounce John back and forth), and that
the cutscene and dialogue data only reference real quest steps. Finally, it
**plays the entire quest line** and verifies that every step can be completed
in its level with the NPCs and enemies that level contains.

---

## Asset notes

The sprites were copied from the pygame project. The original colour-keyed
pure white as transparent, so that white was converted to alpha. Light
textures (`assets/sprites/lights/`) and a 4× copy of the UI sheet (used by the
theme's 9-slice buttons and panels) were generated. Levels and prop scenes
were produced once by a migration script from the original sprite atlas data
(`open_world.json`). From here on, **the scenes are the source of truth**: edit them in the editor.

## Credits

- Programming: Marios Papazoglou, Theophile Aumont (original); Marios Papazoglou (Godot rework)
- Art: Marios Papazoglou
- Story: Manos Danezis
- Music: Thanos Pallis

## AI Usage

Do not use AI if you don't understand its implementations.

## License

Same as the original project: the code may be read and edited, but the
**assets and music may not be reused**.
