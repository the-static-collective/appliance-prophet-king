# NuToaster × Minecraft — semantic cartridge 002

**Source:** [`appliance-prophet-king` / `001-nutoaster-prototype`](https://github.com/the-static-collective/appliance-prophet-king/tree/001-nutoaster-prototype/prototype-001), pinned at commit `a15388ebf2391807559d7cfb334a15c9f3f57992`.

**What this is:** A runnable, inspectable **Minecraft Java 26.1.1** datapack (with a separate **1.20.1 compatibility export**) translating the *relationships* in the NuToaster concept into a large-scale block sculpture: two parallel angled removable-trough *symbols*, three stationary heater/structure regions, guide rods, compression setting markers, and a separate duplicate trough used to illustrate removal.

**What it is not:** The SVG is an annotated **concept drawing**, with cutaway, cross-section, detail and controls on a single page—not an orthographic CAD drawing, scale-bearing floor plan, wiring layout or mechanical blueprint. Its actual dimensions, tolerances, heating behavior, wall forces and build materials are not established. The model's 45° visual staircase follows the written ~45° hypothesis, **not** an angle measured from the sketch (which contains stylized SVG transformations). One Minecraft block is **not one real meter** in this model.

## Run

1. Choose your game's version: `dist/NuToaster_001_Minecraft_Concept_Java_26.1.1.zip` is the **official-server-tested** target; `dist/NuToaster_001_Minecraft_Concept_Java_1.20.1.zip` is a **structurally validated compatibility export** intended for older Java 1.20.1 installations but has not been tested against a live 1.20.1 server. Put the matching ZIP **unextracted** into a **new, empty, backed-up** creative world's `datapacks/` directory. The newest Java game is unlikely to run on macOS 10.14 Mojave; the older export may be easier to run on compatible legacy Minecraft installations, but machine compatibility must be checked separately.
2. Run `/reload` and check `/datapack list`.
3. Choose a clear origin at least 65 × 41 × 29 blocks with loaded chunks. Example: `/execute positioned 0 90 0 run function nutoaster:build`.
4. Walk around the twin white/gray troughs and orange **non-heating** fixed structures; the copper display trough is detached and is **not** a third cooking bay.
5. Optionally run `/execute positioned 0 90 0 run function nutoaster:press_low` (also `press_off`, `press_medium`, `press_high`). These functions only change the four colored front-panel markers; **nothing moves or presses**.

The build writes only `setblock ... keep` to an empty test world; it may skip blocks if the space is occupied, leaving an incomplete model. It does not erase terrain or simulate heat. Display-only mode functions replace four designated front-panel markers. There is no auto build-on-load, unsafe shell, file upload or network requirement. There is no rollback routine: use a disposable save or a backup.

## Source-grounded vs interpretive

| From the repository | Game translation | Remaining unknown |
|---|---|---|
| Two independently removable angled bays | Two separated voxel trays on sloping 1:1 stepped tracks | Physical bay width, length and clearances |
| Left, center and right fixed surrounding heaters | Orange strips and copper middle divider | Heater construction and temperatures |
| Four corner spring guides and optional pressure | Guide bar symbols and OFF / LOW / MEDIUM / HIGH mode indicator blocks | Travel, force, friction; **no game mechanics simulate them** |
| Dirty part deliberately removable | Detached third **sample object** illustrating one removable duplicate | Real removal path and cleanup ergonomics |
| Cold P0 test comes before electric heating | `CONCEPT_ONLY_UNMEASURED_HOLD` provenance disposition | Physical fit and safe construction |

**Next right experiment:** build one non-electrical full-size trough, capture the seven measurements identified in Prototype 001 (mouth, floor, wall height, trough length, insertion clearance, removal clearance, compression travel), and use *those measured values* to create the first dimensionally meaningful voxel/CAD variant. The Minecraft artifact is a design discussion aid, **not** a real appliance plan.

## Build and test (Python 3.10+, standard library only)

```sh
python3 -m unittest discover -s tests -v
python3 generate.py dist
```

The generator produces a deterministic Java datapack ZIP, `SOURCE_CONCEPT.json` with source ancestry/claims/nonclaims and `nutoaster_build.mcfunction` for inspection. Does not depend on game installation or a live Minecraft server. Minecraft binary execution remains **untested here**; only structural validation of generated files has run locally.

## Integration into the wider system

This is a **semantic carrier** to sit beside Abundent Blueprint Bridge 005 (dimension-calibrated building floor plans) and Circuit 004 (in-game observation). A signed reLATTE crossing, Full Measure game receipt, GHoT native execution, physical fabrication, or proof of mechanical function is **not** created by compiling this cartridge. Any such future bridge needs its own explicit request, operator authority and reproducible test.
