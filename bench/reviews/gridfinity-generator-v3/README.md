# Continuous outer frame revision

Owner correction: remove per-cell exterior notches and discontinuous corner
transitions. One outside frame has straight sides/rear joins and tangent R5
front corners. The front beam and webs are clipped to that outline.
Bin pockets and shared internal ribs retain their earlier profiles.

Nine native cases: 1×1, 2×1, 2×2, 3×1, 4×1, intentionally tight,
+5°, −30°, and maximum +0.20 mm clearance. Each is one valid solid,
STEP readback has zero symmetric volume difference, and saved STL coordinate
edges pass closure, winding, connected-surface and bed checks.
All preserve board-side connectors and continuous 5.4 mm roots.
Nonnegative-clearance cases pass 13 normal-to-seat lift positions per cell.
The negative-clearance case intentionally intersects the reference foot.

Beam core containment passes between the outer peg columns. Thickness is
1.9 mm at zero clearance, 1.85 mm at maximum clearance; depth is the selected
beam depth. The first eight runs used the equivalent fixed 1.9 mm gate for
their nonpositive clearances. The final maximum-clearance run uses the
parameterized gate; geometry did not change between those runs.

At zero clearance the outer cell span46 mm and pocket41.9 mm leave2.05 mm
straight rim. R5 outside / R3.95 pocket give approximately2.464 mm diagonal
corner thickness. Frame widths46/88/130/172 mm remain within lane envelopes
48.8/99.6/150.4/175.8 mm.

Rebuild each case from CHECKS.json parameters (only the six input keys in the
source README). Render scenes expect regenerated case/shelf-print.stl beside
them. Images use actual native geometry. No physical fit/load, slicer support,
retention or creep qualification is inferred. Earlier G-code remains old CAD.
