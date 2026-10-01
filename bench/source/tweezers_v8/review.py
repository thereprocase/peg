"""Check actual meshes, neighbours and translation paths; render CAD evidence."""
from pathlib import Path
import argparse,json,math
import numpy as np
import trimesh
from trimesh.collision import CollisionManager
import matplotlib
matplotlib.use('Agg')
from holder import PREFIX,HEELS,R

def render(parts,path,title,view=(60,125),labels=None):
    # Use a depth-buffered CAD render: large receiver faces must correctly
    # hide rear pegs and ribs. A painter's triangle sort cannot guarantee that.
    import vtk
    from vtk.util.numpy_support import numpy_to_vtk,numpy_to_vtkIdTypeArray
    import matplotlib.colors as mc
    from PIL import Image,ImageDraw,ImageFont
    renderer=vtk.vtkRenderer();renderer.SetBackground(*mc.to_rgb('#253139'))
    window=vtk.vtkRenderWindow();window.SetOffScreenRendering(1);window.SetSize(1540,1260);window.AddRenderer(renderer)
    for m,color in parts:
        points=vtk.vtkPoints();points.SetData(numpy_to_vtk(np.asarray(m.vertices,dtype=np.float64),deep=True))
        cells=vtk.vtkCellArray();cells.SetCells(len(m.faces),numpy_to_vtkIdTypeArray(np.c_[np.full(len(m.faces),3),m.faces].astype(np.int64).ravel(),deep=True))
        data=vtk.vtkPolyData();data.SetPoints(points);data.SetPolys(cells)
        normals=vtk.vtkPolyDataNormals();normals.SetInputData(data);normals.SetFeatureAngle(35);normals.SplittingOn();normals.Update()
        mapper=vtk.vtkPolyDataMapper();mapper.SetInputConnection(normals.GetOutputPort())
        actor=vtk.vtkActor();actor.SetMapper(mapper);actor.GetProperty().SetColor(*mc.to_rgb(color));actor.GetProperty().SetInterpolationToPhong();actor.GetProperty().SetAmbient(.3);actor.GetProperty().SetDiffuse(.7);renderer.AddActor(actor)
    v=np.concatenate([m.vertices for m,_ in parts]);centre=(v.min(0)+v.max(0))/2
    elev,azim=np.deg2rad(view);direction=np.array([np.cos(elev)*np.cos(azim),np.cos(elev)*np.sin(azim),np.sin(elev)])
    camera=renderer.GetActiveCamera();camera.SetPosition(*(centre+direction*np.ptp(v,axis=0).max()*3));camera.SetFocalPoint(*centre);camera.SetViewUp(0,0,1);camera.ParallelProjectionOn();renderer.ResetCamera();camera.SetParallelScale(camera.GetParallelScale()*1.1)
    window.Render();capture=vtk.vtkWindowToImageFilter();capture.SetInput(window);capture.Update();writer=vtk.vtkPNGWriter();writer.SetFileName(str(path));writer.SetInputConnection(capture.GetOutputPort());writer.Write();window.Finalize()
    im=Image.open(path).convert('RGB');draw=ImageDraw.Draw(im)
    fonts=Path(matplotlib.get_data_path())/'fonts'/'ttf'
    font=str(fonts/'DejaVuSans.ttf');bold=str(fonts/'DejaVuSans-Bold.ttf')
    draw.rectangle((0,0,1540,95),fill='#253139');draw.text((60,30),title,font=ImageFont.truetype(bold,34),fill='#e7eeeb')
    if labels:
        draw.rectangle((0,1180,1540,1260),fill='#253139');draw.text((60,1200),labels,font=ImageFont.truetype(font,22),fill='#c8d8d4')
    im.save(path)
    return

def main():
    p=argparse.ArgumentParser();p.add_argument('directory',type=Path);p.add_argument('--mount-motion',type=Path);args=p.parse_args();d=args.directory
    holder=trimesh.load(d/(PREFIX+'__installed.stl'))
    tools=[trimesh.load(d/f'{PREFIX}__reference-tool-{i+1}.stl') for i in range(4)]
    manager=CollisionManager();manager.add_object('holder',holder)
    rest=[];paths=[];tipclear=[];settle=[]
    for i,m in enumerate(tools):
        others=CollisionManager();others.add_object('holder',holder)
        for j,n in enumerate(tools):
            if i!=j:others.add_object(f'neighbour-{j}',n)
        cache={}
        def distance(pos):
            key=tuple(pos)
            if key not in cache:
                q=np.eye(4);q[:3,3]=pos
                cache[key]=float(others.min_distance_single(m,transform=q))
            return cache[key]
        segments=[(np.array([0.,0.,0.]),np.array([0.,0.,5.])),(np.array([0.,0.,5.]),np.array([-30.,0.,5.]))]
        def check(a,b,depth=0):
            da,db=distance(a),distance(b);length=float(np.linalg.norm(b-a))
            assert min(da,db)>1e-5, (i,a,b,da,db)
            if da+db>length+.08:return min(da,db,(da+db-length)/2)
            assert depth<20,(i,a,b,da,db)
            mid=(a+b)/2
            return min(check(a,mid,depth+1),check(mid,b,depth+1))
        bound=min(check(a,b) for a,b in segments)
        paths.append({'slot':i+1,'translation_waypoints_mm':[[0,0,0],[0,0,5],[-30,0,5]],
                      'distance_evaluations':len(cache),'continuous_translation_clearance_lower_bound_mm':bound,
                      'minimum_evaluated_mesh_distance_mm':min(cache.values()),'passed':True})
        rest.append(distance(np.zeros(3)))
        local=(m.vertices-HEELS[i])@R
        mask=np.all(local[m.faces][:,:,1]>=108,axis=1)
        tips=m.submesh([np.flatnonzero(mask)],append=True)
        tipclear.append(float(manager.min_distance_single(tips)))
        # Establish a positive body stop under gravity. This is geometry,
        # not an elastic/contact-force prediction or a print qualification.
        first=None
        for drop in np.arange(.25,5.01,.25):
            q=np.eye(4);q[2,3]=-drop
            if manager.in_collision_single(m,transform=q):first=float(drop);break
        assert first is not None,(i,'No body seat under gravity')
        settle.append(first)
    report_path=d/(PREFIX+'__design-and-checks.json');report=json.loads(report_path.read_text())
    report['tool_mesh_checks']={'open_rest_holder_and_neighbour_clearance_mm':rest,'point_region_holder_distance_mm':tipclear,
       'gravity_body_stop_detected_by_vertical_drop_mm':settle,'removal_paths':paths,
       'method':'Triangle-mesh distances with rigid translation Lipschitz bounds between adaptively subdivided endpoints. Same reversed path for insertion. Valid only for the supplied nominal open-pose meshes; excludes elasticity, tolerance and hands.',
       'tip_down_axis_in_world':R[:,1].tolist()}
    if args.mount_motion:
        import sys
        sys.path.append(str(Path(__file__).resolve().parents[2]/'reference'))
        from host_envelope import certify_host_polygon
        from scipy.spatial import ConvexHull
        v=holder.vertices[holder.vertices[:,1]>=5.149][:,1:];v=v[ConvexHull(v).vertices]
        motion=json.loads(args.mount_motion.read_text());cases=[]
        for case in motion['cases']:
            cert=certify_host_polygon([s['pose'] for s in case['samples']],v.tolist());assert cert['passed']
            cases.append({'board_thickness_mm':case['board_thickness_mm'],'new_front_host_envelope':cert})
        report['new_host_mount_check']={'scope':'Added front host only, on continuously interpolated v7 pose paths. Unchanged interfering pegs retain the v7 compliance assumptions.','projected_convex_hull_yz_mm':v.tolist(),'cases':cases}
    report_path.write_text(json.dumps(report,indent=2)+'\n')
    teal='#4ca191';steel='#ccd2d5'
    render([(holder,teal),*[(m,steel) for m in tools]],d/(PREFIX+'__loaded.png'),'v8 · tips down · long body cradles',labels='Lift 5 mm, then move left. The open arms and bent points stay free.')
    render([(holder,teal)],d/(PREFIX+'__empty.png'),'v8 · continuous support, low guide rails')
    render([(holder,teal)],d/(PREFIX+'__rear.png'),'The original 14-point v7 mount',view=(12,-65))
    guide=trimesh.load(d/'cradle-local.stl');one=tools[0].copy();one.vertices=(one.vertices-HEELS[0])@R
    render([(guide,teal),(one,steel)],d/(PREFIX+'__detail.png'),'Body contact · open arms · free points',view=(14,-64),labels='Closer side guides cover 19 mm of the broad body. No closing jaw or point floor.')
    printmesh=trimesh.load(d/(PREFIX+'__print-right-cheek.stl'))
    render([(printmesh,teal)],d/(PREFIX+'__print.png'),'Right-cheek STL · supports required',view=(30,-55))
    test=trimesh.load(d/(PREFIX+'__single-throat-test__print-right-cheek.stl'))
    render([(test,teal)],d/(PREFIX+'__test-piece.png'),'Print this single throat first',view=(32,-45),labels='Check seating, rocking and the lift/left path before printing the four-slot station.')
    print(json.dumps(report['tool_mesh_checks'],indent=2),flush=True)

if __name__=='__main__':main()
