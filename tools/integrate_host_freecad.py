"""Replace the reference handle with a host; never alter the board-side pegs.

Run with FreeCAD's Python interpreter. This example demonstrates integration,
not a load-rated holder or a print orientation. Coordinates are millimetres.
"""
from pathlib import Path
import json
import FreeCAD as App
import Part

ROOT = Path(__file__).resolve().parents[1]
FACE_Y = 0.15


def box(x0, y0, z0, x1, y1, z1):
    return Part.makeBox(x1-x0, y1-y0, z1-z0, App.Vector(x0,y0,z0))


def receive_pegs(reference, host, embed=1.25):
    """Remove the handle, extend the exact cut sections *inside* the host.

    embed is Boolean overlap, not a prescribed structural wall thickness.
    The caller must engineer the surrounding host and its load path.
    """
    if embed <= 0:
        raise ValueError('Positive buried overlap required')
    bounds = reference.BoundBox
    rear = box(bounds.XMin-1, bounds.YMin-1, bounds.ZMin-1,
               bounds.XMax+1, FACE_Y, bounds.ZMax+1)
    functional = reference.common(rear)
    receiving = []
    for face in functional.Faces:
        bb = face.BoundBox
        if abs(bb.YMin-FACE_Y)<1e-7 and abs(bb.YMax-FACE_Y)<1e-7:
            receiving.append(face.extrude(App.Vector(0,embed,0)))
    if len(receiving) != 2:
        raise ValueError('Expected the upper and lower shaft sections')
    for extension in receiving:
        if extension.cut(host).Volume > 1e-6:
            raise ValueError('The host must fully bury both shaft continuations')
    result = host.multiFuse([functional]+receiving).removeSplitter()
    if not result.isValid() or len(result.Solids)!=1:
        raise ValueError('The integrated holder must be one valid solid')
    actual_rear = result.common(rear)
    difference = actual_rear.cut(functional).Volume + functional.cut(actual_rear).Volume
    if difference > 1e-6:
        raise ValueError('Board-side functional geometry changed')
    return result, {'board_side_difference_mm3':difference,
                    'buried_overlap_mm':embed, 'single_valid_solid':True}


def example(output):
    output.mkdir(parents=True,exist_ok=True)
    reference = Part.read(str(ROOT/'cad/conformal/conformal_120.step'))
    allowed = Part.read(str(ROOT/'cad/conformal/host-envelope/allowed_host_volume.step'))
    # Deliberately plain demonstration blank: rear face starts at the board,
    # not at the old handle's Y=4.50 front. Design a real holder in its place.
    host = box(-24,FACE_Y,-40,24,50,35).common(allowed)
    assert host.cut(allowed).Volume < 1e-6
    result, report = receive_pegs(reference,host)
    result.exportStep(str(output/'integration-example.step'))
    reread = Part.read(str(output/'integration-example.step'))
    assert reread.isValid() and len(reread.Solids)==1
    report.update(host_outside_envelope_mm3=host.cut(allowed).Volume,
                  scope='Integration geometry only; strength, printing and fit not qualified')
    (output/'integration-example.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))


if __name__ == '__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'render-preview/host-integration')
    example(parser.parse_args().output)
