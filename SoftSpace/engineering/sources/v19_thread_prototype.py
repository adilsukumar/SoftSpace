"""Nominal helical prototype threads, not a certified ISO tolerance-class model."""
import sys,math,json
from pathlib import Path
P=Path(__file__).parent;sys.path.insert(0,str(P/'cad-validation-libraries'))
from OCP.gp import gp_Pnt,gp_Dir,gp_Ax2,gp_Ax3,gp_Pnt2d,gp_Dir2d
from OCP.Geom import Geom_CylindricalSurface
from OCP.Geom2d import Geom2d_Line
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge,BRepBuilderAPI_MakeWire,BRepBuilderAPI_MakePolygon
from OCP.BRepOffsetAPI import BRepOffsetAPI_MakePipeShell
from OCP.BRepLib import BRepLib
from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder,BRepPrimAPI_MakeBox,BRepPrimAPI_MakePrism
from OCP.BRepAlgoAPI import BRepAlgoAPI_Fuse,BRepAlgoAPI_Cut,BRepAlgoAPI_Common
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.STEPControl import STEPControl_Writer,STEPControl_AsIs
from OCP.gp import gp_Vec
def cylinder(radius,y,length):return BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(0,y,0),gp_Dir(0,1,0)),radius,length).Shape()
def boolean(cls,a,b):
 op=cls(a,b);assert op.IsDone();return op.Shape()
def helix_ridge(y,length,root,crest,basewidth=.62,crestwidth=.0875):
 pitch=.7;start=y-pitch;extent=length+2*pitch;radius=1.8;surface=Geom_CylindricalSurface(gp_Ax3(gp_Pnt(0,start,0),gp_Dir(0,1,0),gp_Dir(1,0,0)),radius);direction=gp_Dir2d(1,pitch/(2*math.pi));line=Geom2d_Line(gp_Pnt2d(0,0),direction);theta=extent/pitch*2*math.pi;edge=BRepBuilderAPI_MakeEdge(line,surface,0,theta/direction.X()).Edge();BRepLib.BuildCurves3d_s(edge);wire=BRepBuilderAPI_MakeWire(edge).Wire();profile=BRepBuilderAPI_MakePolygon()
 for r,dy in [(root,-basewidth/2),(crest,-crestwidth/2),(crest,crestwidth/2),(root,basewidth/2)]:profile.Add(gp_Pnt(r,start+dy,0))
 profile.Close();pipe=BRepOffsetAPI_MakePipeShell(wire);pipe.SetMode(True);pipe.Add(profile.Wire());pipe.Build();assert pipe.IsDone();assert pipe.MakeSolid();shape=pipe.Shape();clip=BRepPrimAPI_MakeBox(gp_Pnt(-3,y,-3),6,length,6).Shape();return boolean(BRepAlgoAPI_Common,shape,clip)
def bolt(shoulder):
 shaft=cylinder(2,0,shoulder);head=cylinder(3.5,-4,4);core=cylinder(1.5706,shoulder-.1,8.1);ridge=helix_ridge(shoulder+.01,7.99,1.54,2);thread=boolean(BRepAlgoAPI_Fuse,core,ridge);return boolean(BRepAlgoAPI_Fuse,boolean(BRepAlgoAPI_Fuse,shaft,head),thread)
def nut(y,height,shoulder):
 if shoulder!=37:
  from OCP.gp import gp_Trsf
  from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
  shift=gp_Trsf();shift.SetTranslation(gp_Vec(0,shoulder-37,0));return BRepBuilderAPI_Transform(nut(round(y-shoulder+37,6),height,37),shift,True).Shape()
 p=BRepBuilderAPI_MakePolygon();radius=7/math.sqrt(3)
 for k in range(6):p.Add(gp_Pnt(radius*math.cos(k*math.pi/3),y,radius*math.sin(k*math.pi/3)))
 p.Close();from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace
 body=BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(p.Wire()).Face(),gp_Vec(0,height,0)).Shape();body=boolean(BRepAlgoAPI_Cut,body,cylinder(1.65,y-.1,height+.2));tool=helix_ridge(shoulder+.01,7.99,1.60,2.06,.66,.12)
 shape=boolean(BRepAlgoAPI_Cut,body,tool)
 if not BRepCheck_Analyzer(shape).IsValid():
  from OCP.ShapeFix import ShapeFix_Shape
  fix=ShapeFix_Shape(shape);fix.Perform();shape=fix.Shape()
 return shape
if __name__=='__main__':
 from audit_v14_motion import mass
 O=P/'engineering-v19-results';O.mkdir(exist_ok=True);s=bolt(37);n=nut(37.6625,3.2,37);j=nut(40.8625,2.2,37);assert all(BRepCheck_Analyzer(x).IsValid() for x in [s,n,j]);overlaps=[mass(boolean(BRepAlgoAPI_Common,s,x)) for x in [n,j]];assert max(overlaps)<1e-6,overlaps
 for name,shape in [('pin',s),('nut',n),('jam_nut',j)]:
  w=STEPControl_Writer();w.Transfer(shape,STEPControl_AsIs);w.Write(str(O/('threaded_'+name+'_child_trial.step')))
 (O/'thread_trial_status.json').write_text(json.dumps(dict(bolt_valid=True,nut_valid=True,jam_nut_valid=True,bolt_nut_overlap_mm3=overlaps,thread_pitch_mm=.7,scope='Idealised helical prototype only,not certified ISO tolerances or thread strength qualification'),indent=2));print('Helical pin and two nuts valid with positive nominal thread clearance')
