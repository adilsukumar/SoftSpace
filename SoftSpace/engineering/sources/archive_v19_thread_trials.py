import sys,json,hashlib
from pathlib import Path
P=Path(__file__).parent;sys.path.insert(0,str(P/'cad-validation-libraries'))
from OCP.STEPControl import STEPControl_Reader
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_SOLID
from OCP.BRepCheck import BRepCheck_Analyzer
O=P/'engineering-v19-results';D=O/'rejected-thread-trials';D.mkdir(exist_ok=True);rows=[]
for f in sorted((O/'final-CAD').glob('*_nominal.step')):
 reader=STEPControl_Reader();reader.ReadFile(str(f));reader.TransferRoots();shape=reader.OneShape();e=TopExp_Explorer(shape,TopAbs_SOLID);valid=[]
 while e.More():valid.append(BRepCheck_Analyzer(e.Current()).IsValid());e.Next()
 target=D/f.name;assert f.parent.resolve()==(O/'final-CAD').resolve() and target.parent.resolve()==D.resolve();digest=hashlib.sha256(f.read_bytes()).hexdigest();f.replace(target);rows.append(dict(file=str(target),sha256=digest,solids=len(valid),BRep_valid=all(valid),expected_connected_solids=1,accepted_for_final_assembly=False))
(D/'trial_audit.json').write_text(json.dumps(dict(trials=rows,decision='Rejected thread trial. A bolt with two disconnected solids is not a manufactured pin even if each solid is valid. No exact-helix trial geometry is in final V19 assemblies.'),indent=2))
