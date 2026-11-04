# NuToaster 003 — provisional measurements, P0 cardboard mockup and dimensioned Minecraft model

**Status: `HYPOTHETICAL_UNMEASURED_HOLD` — exactly seven invented starting dimensions.**

This experiment adds an intentionally fictional dimension set to the qualitative NuToaster Prototype 001 schematic. Source repo: `the-static-collective/appliance-prophet-king`, `001-nutoaster-prototype`, commit `a15388ebf2391807559d7cfb334a15c9f3f57992`. That source specified the *kinds* of measurements and the candidate ~45° angle; it did **not** specify the numeric sizes. Nothing in this directory asserts those sizes were measured, inferred from SVG pixels, built, or tested as an appliance.

## Seven made-up design choices

| Dimension | Guess | What it means |
| --- | ---: | --- |
| Mouth inner width | **140 mm** | Top clear opening of a single trough, compression OFF |
| Floor inner width | **118 mm** | Flat bottom inside width |
| Wall vertical height | **70 mm** | Vertical separation of the top lip and inner floor (not slanted sheet width) |
| Interior trough length | **240 mm** | Distance along the long side / tilt axis |
| Insertion clearance | **8 mm each side** | Hypothetical gap between tray and a surrounding cold chassis |
| Removal clearance | **280 mm along tilt axis** | Proposed path to extract a whole tray without obstruction; actual geometry not verified |
| Compression travel | **10 mm each side** | Proposed future movable-wall displacement, **not included in cold P0** |

Source hypothesis: approximately **45°** incline. Additional independent guess for future chassis layout: **20 mm center divider**. Everything here is adjustable, and *none* is a known physical requirement. Compression OFF leaves 140 mm mouth; projected fully inward mouth 120 mm, slightly wider than the 118 mm floor. Whether that motion works in a spring mechanism is unknown.

The provisional developed cardboard side-panel width is `sqrt(70² + 11²) ≈ 70.86 mm`; an open-ended one-piece net is about `259.72 mm wide × 240 mm long`, which fits on A3 landscape. **Not** a sheet-metal cutting pattern: real bends, sheet thickness, end closures, spring mounts, thermal isolation and all manufacturing details remain undefined.

## Clickable GUI / printable P0

On Mac, double-click `open-nutoaster-mac.command`, or open `tweak.html` directly in a browser (it needs no Python). Click **Bread**, **Burger / wide**, or **Compact**, optionally adjust the seven sliders, then click **Print A3 cold-trough template**. The exported SVG specifies a 420×297 mm page; print at **100%** and check the **100 mm verification bar**. Fold along blue dashed lines, tape externally, use only with cold non-food test objects. No end caps, no liquids, no electricity, no cooking. This is a disposable shape test.

The GUI can export a JSON with your revised guesses. The generated `assumptions.json` is the versioned, machine-readable default source. To reproduce the release from a checkout: `python3 prototype-003-provisional/generate.py`. To rebuild from an exported custom preset: `python3 prototype-003-provisional/generate.py output-folder --spec your-downloaded.json`. Python 3.10+ stdlib; no network. The 10 mm voxel grid rounds modified geometry: the JSON preserves exact invented inputs; Minecraft represents them only approximately.

## Minecraft rehearsal

The generator produces version-specific Java datapacks for **1.20.1** and **26.1.1**. Both represent the *hypothetical* trough at approximately **10 mm of proposed source geometry per 1 Minecraft block**, so this is an enlarged visual analogy (not one real meter per block). Voxel snapping is approximate. The raw 7 numbers survive exactly in `SOURCE_GUESSES.json`. The two installed bays, detached sample tray, orange heater symbols, central structural divider and pressure-setting indicators are purely visual. Heat and pressure do not operate.

To try in Minecraft Java:

1. Back up; create a **brand-new empty flat creative** world. Never use a valued, shared or inhabited world.
2. Copy the matching generated `.zip` into the world's `datapacks/` directory **without unzipping**.
3. Enter `/reload`, then `/datapack list`.
4. Inspect and load an empty region at least 66×45×42 blocks. With world command permissions, execute `/execute positioned 0 90 0 run function nutoaster_p0:build`.
5. Optional demonstration: `/execute positioned 0 90 0 run function nutoaster_p0:press_low`; also `press_off`, `press_medium`, `press_high`. **Only four color markers change.**

No auto-build, networking, unsafe external program execution or undo is included. Build uses `setblock ... keep` and may leave an incomplete sculpture in occupied terrain. The 1.20.1 output is syntactically generated and tested offline but has **not** been verified on a live 1.20.1 server; likewise, the 26.1.1 file isn't claimed real-game tested until CI actually completes. Production hardware/safety validation is explicitly out of scope.

## What to measure when the actual object exists

First make one cardboard trough. Put a **cold** bread-sized mock and burger-sized object into it. Record real mouth/floor/height/length, side insertion clearance against a dummy chassis, withdrawal path length and the useful future wall displacement. Replace hypothetical values with real P0 measurements, marked `MEASURED_COLD_P0`, in a *new revision*; never rewrite these guesses as historical fact.

**Useful next question:** Does a 140 mm mouth and 240 mm length comfortably accept the intended foods, and can the tray be withdrawn along a 45° path without hitting its neighbor? A cold P0 cannot establish heat transfer, food safety, coil design, force, hygiene or electrical safety.
