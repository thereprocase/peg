Tweezers v8: tip-down long body cradles
=====================================

Store, insert and remove with the points DOWN. Grasp the broad rear end.
Lift vertically 5 mm, then move left 30 mm. Insert along the reverse path.
The holder supports the lower arm's broad outer face and guides its edges;
the upper arm has no closing jaw. The throat ends before the slender working
end. There is no floor under the points. This is a prototype for the supplied
bent tweezer, not a universal four-tool fit.

The v7 board receiver, two upper hooks and twelve straight locators are
retained by an exact CAD intersection. The shared e586ab4ff6 peg fit is
unchanged. It still uses interference/compliance; the new front body does
not turn that into a rigid collision-free or physically qualified mount.

Design dimensions
-----------------
122.76 mm measured tweezer length; 1.17 mm TOTAL fused rear thickness;
1.31 mm TOTAL aft thickness slightly forward. The 1.47 mm photo is a
separated forward arm. Joined length, exact measuring stations, outline
and natural opening are reconstructed estimates; see parameters.json.

58 mm contoured body support, from 6 to 64 mm forward of the heel.
Closer lateral guides over stations 42..61 mm, 0.08 mm per edge.
Aft lateral clearance 0.35 mm per edge; lower-face allowance 0.35 mm.
2.4 mm walls and 0.6 mm rounded rail corners. The low rails allow a short
lift before the left departure; they do not form an opposed spring clamp.
The tight lateral allowance should be checked on the small test piece.

48.8 mm mounting width, original 42 mm slot spacing and 40 degree tilt.
Full installed bounds: 48.8 x 116.98 x 227.0 mm (X/Y/Z). The long throats
extend farther forward and higher than v7 to reach the upper body. The
points remain within the original receiver's lower height in the nominal
loaded arrangement. All four slots repeat the same measured tweezer.

Printing and fit
----------------
Print the SINGLE-THROAT TEST PIECE first. Hold it at the installed angle;
check that the tool settles on the body, stays open, rocks acceptably and
clears both rails with a short lift. Check that no point touches plastic.
Do not force a tight fit; increase the side_clearance parameter in holder.py
if needed. Only print the full station after this check.

STL units are millimetres. The supplied STL is on its right cheek, Z=0.
The full part fits a 256 mm square plate geometrically (227 x 116.98 mm),
with supports and a brim. The coupon has the same throat, without a mount.
Use the intended printer, plate and filament profile. Remove support from
the guide surfaces and check for burrs before trying the real tool.

OrcaSlicer 2.4.2 geometry review: P1S 0.4, 0.20 mm Standard, three walls,
15% infill, normal supports on the plate, 5 mm outer brim. Generic PLA
system preset used for geometry review only. Full station sliced without
reported warnings; estimated 3 h 31 min, 135 g including support/brim.
No review G-code or machine-ready job is published. The included JSON
records settings and results; no physical fit/load/wear testing is claimed.

Checks and reproduction
-----------------------
Installed, print and coupon CAD are valid single solids. STLs are closed
with consistent outward winding; STEP re-import volume matches. The
unchanged mounting/receiver region has zero symmetric volume difference.
Nominal open-pose tools have 0.078 mm minimum holder/neighbour clearance.
Point-region clearance is at least 3.02 mm at rest. A downward displacement
of 0.75 mm reaches the body support in the rigid nominal model. This is
not an elastic seating or contact-force prediction.

Removal uses actual triangle meshes with neighbours present, a 5 mm lift
and 30 mm left motion. Adaptive endpoint distances bound clearance over
each complete rigid translation, not only sampled poses. The conservative
bound is 0.0405 mm. These results apply to the reconstructed nominal tool,
not printing tolerance, hands, bending or a different tweezer. New host
board-front clearance was separately checked on the existing v7 mounting
pose paths; the original peg compliance assumptions remain in effect.

In the self-contained CAD bundle, run with Python 3.12:
  python -m venv .venv
  .venv/bin/pip install -r requirements.txt
  .venv/bin/python holder.py --output regenerated
  .venv/bin/python review.py regenerated

In the repository, give --baseline the v7 installed STEP from its original
release (holders-2026-09-16). Its required SHA256 is
2abdd83699589dac57290c444aeb298cfc429a8d2d4eb9effbe83d5bf0c20f37.
The bundle includes this exact input, source, fitted tool parameters,
open/closed reference STL models, printable exports, previews and checks.
Raw photos and photogrammetry scans are excluded.
