# Generic toolpath check

We sliced the side and upright exports with **CuraEngine 5.0.0**, using the Cura 5.0.0 generic FDM definitions. This is a geometric toolpath review, not a Bambu P1S profile or a physical print test. The generated GCode stays outside the deliverable package and must not be sent to a printer.

## Results

| Item | Side orientation | Upright orientation |
|---|---:|---:|
| Nozzle / layer | 0.4 / 0.2 mm | 0.4 / 0.2 mm |
| Nominal wall width | 0.45 mm | 0.45 mm |
| Walls | 5 | 2 |
| Infill | 30% requested, geometry mostly walls | 100%, lines, 0.45 mm spacing |
| Automatic supports | Off | Off |
| Layers | 20 | 173 |
| Connected model footprints on first layer | 1 | 1 |
| Wholly detached deposition components found | 0 | 0 |

The upright check used a 6 mm brim, represented by fourteen 0.45 mm loops. A complete host may provide sufficient bed contact without that standalone-anchor brim. Cura preserves the four 0.50 mm membranes as single variable-width paths. The sampled web tips advance 0.20 mm per 0.20 mm layer and connect to the spine.

The first lower roof at Z = 3.2 mm uses X-directed skin lines with 2.241 mm centerline length. The first major upper roof at Z = 28.2 mm uses X-directed bridge skin with 2.650 mm centerline length. The model's clear space between membrane faces is 2.70 mm; centerline lengths differ because Cura also lays perimeter paths and overlaps infill with them.

![Actual generic Cura toolpaths](visuals/upright-actual-toolpaths.png)

## Slicer choice that matters

**Do not blindly apply five walls to the upright roofs.** Our first trial did that: the narrow 4 mm width filled with nested perimeter loops, leaving no clean X-directed bridge skin. The successful review used two walls, solid line infill, no skin outline, bridge detection, and a 1 mm minimum bridge-wall length. For an integrated host, apply this strategy with a local modifier around the upright anchor and inspect the underside layers. Keep five walls for the side-printed anchor. A different slicer may need different bridge controls.

This review does not establish equal strength between orientations. The upright build still relies more heavily on layer adhesion. Supports solve deposition geometry; they do not recreate the continuous in-layer hook profile of the side orientation. The final host, material, cooling, and load leverage require print and load checks.

## Scope of the component check

We reconstructed each deposited line's XY width from extrusion volume divided by path length and layer height, then combined the line envelopes. Excluding the brim, each first layer contains one connected model footprint. Across all layers, every deposited component larger than 0.01 mm² intersects the previous layer's deposited footprint after a 0.20 mm horizontal expansion. This catches wholly detached components. It does not validate every unsupported segment, sag, thermal behavior, nozzle contact, or bond strength. The bridge directions were checked separately in actual extrusion moves.

## Exact inputs and reproduction

`slicer_check.json` contains both complete explicit settings dictionaries, STL SHA-256 hashes, software package identifiers, and the result metrics. The definitions supply all other default settings. The binary came from Ubuntu `cura-engine_5.0.0-5ubuntu1_amd64.deb`; definitions came from `cura_5.0.0-6_all.deb`.

To recreate the geometry review with those Cura definitions, set `CURA_ENGINE` to the engine executable and `CURA_DEFINITIONS` to the directory containing `fdmprinter.def.json` and `fdmextruder.def.json`. Run the following from this package directory. Output goes to a temporary scratch directory, never into a printer queue.

```python
import json, os, pathlib, subprocess, tempfile
root = pathlib.Path.cwd()
report = json.loads((root / "slicer_check.json").read_text())
defs = pathlib.Path(os.environ["CURA_DEFINITIONS"])
env = os.environ.copy()
env["CURA_ENGINE_SEARCH_PATH"] = str(defs)
review_dir = pathlib.Path(tempfile.mkdtemp(prefix="pegboard-gcode-review-"))
for name, filename, settings_key in [
    ("side", "anchor_default_3p94mm.stl", "settings_flat_complete"),
    ("upright", "anchor_upright_supported.stl", "settings_upright_complete"),
]:
    args = [os.environ["CURA_ENGINE"], "slice", "-m2",
            "-j", str(defs / "fdmprinter.def.json")]
    for key, value in report[settings_key].items():
        value = str(value).lower() if isinstance(value, bool) else str(value)
        args.extend(["-s", f"{key}={value}"])
    args.extend(["-e0", "-j", str(defs / "fdmextruder.def.json"),
                 "-s", "machine_nozzle_size=0.4",
                 "-s", "material_diameter=1.75",
                 "-l", str(root / "cad" / filename),
                 "-o", str(review_dir / f"{name}_REVIEW_ONLY.gcode")])
    result = subprocess.run(args, env=env, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, text=True, check=True)
    (review_dir / f"{name}.log").write_text(result.stdout)
print(review_dir)
```

The generic settings include temperatures and machine defaults only because the engine needs a complete slicing context. They are not recommendations for a printer or filament. Inspect the user's own printer profile and slice the final host before printing.
