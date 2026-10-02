"""Depth-buffered renders of the v11 build (vtk, as v8/v10's review renders).

Run with the CadQuery/trimesh Python (cadpy): python render.py BUILD_DIR
"""
from pathlib import Path
import sys

import numpy as np
import trimesh
import matplotlib
matplotlib.use('Agg')

NAME = 'part-solder-modules-tweezers__v11__edge-trays-right-cheek__fit-pf02c9-hoop5'
TEAL, STEEL, AMBER = '#4ca191', '#ccd2d5', '#e0a040'


def render(parts, path, title, view=(25, 55), labels=None, zoom=1.1, up=(0, 0, 1)):
    import vtk
    from vtk.util.numpy_support import numpy_to_vtk, numpy_to_vtkIdTypeArray
    import matplotlib.colors as mc
    from PIL import Image, ImageDraw, ImageFont
    ren = vtk.vtkRenderer(); ren.SetBackground(*mc.to_rgb('#253139'))
    win = vtk.vtkRenderWindow(); win.SetOffScreenRendering(1); win.SetSize(1540, 1260); win.AddRenderer(ren)
    for m, color in parts:
        pts = vtk.vtkPoints(); pts.SetData(numpy_to_vtk(np.asarray(m.vertices, dtype=np.float64), deep=True))
        cells = vtk.vtkCellArray()
        cells.SetCells(len(m.faces), numpy_to_vtkIdTypeArray(np.c_[np.full(len(m.faces), 3), m.faces].astype(np.int64).ravel(), deep=True))
        poly = vtk.vtkPolyData(); poly.SetPoints(pts); poly.SetPolys(cells)
        nrm = vtk.vtkPolyDataNormals(); nrm.SetInputData(poly); nrm.SetFeatureAngle(35); nrm.SplittingOn(); nrm.Update()
        mapper = vtk.vtkPolyDataMapper(); mapper.SetInputConnection(nrm.GetOutputPort())
        actor = vtk.vtkActor(); actor.SetMapper(mapper)
        prop = actor.GetProperty(); prop.SetColor(*mc.to_rgb(color)); prop.SetInterpolationToPhong()
        prop.SetAmbient(.3); prop.SetDiffuse(.7)
        ren.AddActor(actor)
    v = np.concatenate([m.vertices for m, _ in parts]); centre = (v.min(0)+v.max(0))/2
    el, az = np.deg2rad(view)
    d = np.array([np.cos(el)*np.cos(az), np.cos(el)*np.sin(az), np.sin(el)])
    cam = ren.GetActiveCamera(); cam.SetPosition(*(centre+d*np.ptp(v, axis=0).max()*3)); cam.SetFocalPoint(*centre)
    cam.SetViewUp(*up); cam.ParallelProjectionOn(); ren.ResetCamera(); cam.SetParallelScale(cam.GetParallelScale()*zoom)
    win.Render()
    grab = vtk.vtkWindowToImageFilter(); grab.SetInput(win); grab.Update()
    w = vtk.vtkPNGWriter(); w.SetFileName(str(path)); w.SetInputConnection(grab.GetOutputPort()); w.Write(); win.Finalize()
    im = Image.open(path).convert('RGB'); dr = ImageDraw.Draw(im)
    fonts = Path(matplotlib.get_data_path())/'fonts'/'ttf'
    dr.rectangle((0, 0, 1540, 95), fill='#253139')
    dr.text((60, 30), title, font=ImageFont.truetype(str(fonts/'DejaVuSans-Bold.ttf'), 34), fill='#e7eeeb')
    if labels:
        dr.rectangle((0, 1180, 1540, 1260), fill='#253139')
        dr.text((60, 1200), labels, font=ImageFont.truetype(str(fonts/'DejaVuSans.ttf'), 22), fill='#c8d8d4')
    im.save(path)


def clip(mesh, lo, hi):
    m = mesh
    for ax in range(3):
        n = np.zeros(3); n[ax] = 1
        m = m.slice_plane(np.where(n, lo, 0), n, cap=False)
        m = m.slice_plane(np.where(n, hi, 0), -n, cap=False)
    return m


def main(d):
    holder = trimesh.load(d/f'{NAME}__installed.stl')
    tools = [trimesh.load(d/f'{NAME}__tool-{k}.stl') for k in range(1, 5)]
    wedges = [trimesh.load(d/f'{NAME}__wedge-{k}__installed.stl') for k in range(1, 5)]
    render([(holder, TEAL)]+[(w, AMBER) for w in wedges]+[(t, STEEL) for t in tools], d/f'{NAME}__loaded.png',
           'v11 · tweezers on edge · 15° trays · glued wedges',
           view=(28, 58), labels='Points first along the floor until the wedge meets the crotch; the cant leans each tool on two ribs.')
    render([(holder, TEAL)]+[(w, AMBER) for w in wedges], d/f'{NAME}__empty.png',
           'v11 · empty: floors, lean ribs, wedges (amber, glued)', view=(28, 58))
    render([(holder, TEAL)]+[(t, STEEL) for t in tools], d/f'{NAME}__front.png',
           'v11 · from the front, facing the pegboard', view=(8, 90), zoom=1.0,
           labels='Floors rise 15° to the left; each tool leans right onto the cheek ribs.')
    hoop = clip(holder, np.array([5.0, -12.0, -160.0]), np.array([20.5, 1.0, -144.5]))
    render([(hoop, TEAL)], d/f'{NAME}__hoop.png', 'v11 bottom peg · PF07 #5 hoop, thinner nose, root gusset',
           view=(70, 200), zoom=1.15, labels='Hoop lies in the cheek plane, so it flexes in the print layers.')
    pr = trimesh.load(d/f'{NAME}__print-right-cheek.stl')
    w = trimesh.load(d/f'{NAME}__wedge__print.stl')
    plate = [(pr, TEAL)]
    x0 = pr.bounds[1][0]+6
    for k in range(4):
        wk = w.copy(); wk.apply_translation([x0, 5+k*8.0-w.bounds[0][1], -w.bounds[0][2]]); plate.append((wk, AMBER))
    render(plate, d/f'{NAME}__print.png', 'Print: right cheek on the bed, four wedges alongside',
           view=(35, -60), labels='Only the pegs print in the air. Glue the wedges into the floor slots with CA.')


if __name__ == '__main__':
    main(Path(sys.argv[1]))
