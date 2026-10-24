from pathlib import Path
import shutil
P=Path(__file__).resolve().parent;backup=P/'package-history/v24-source-before';backup.mkdir(exist_ok=True)
for name in ['v12_geometry.py','audit_v14_motion.py']:
 f=P/name;s=f.read_text(encoding='utf-8-sig')
 if 'from project_paths import verified_source' in s:continue
 if not (backup/name).exists():shutil.copy2(f,backup/name)
 if name=='v12_geometry.py':
  old="source=Path(row['file']);assert hashlib.sha256(source.read_bytes()).hexdigest()==row['sha256']";assert old in s;s=s.replace(old,"source=verified_source(row)")
 else:
  old="assert hashlib.sha256(Path(row['file']).read_bytes()).hexdigest()==row['sha256'];r=STEPControl_Reader();r.ReadFile(row['file']);r.TransferRoots()";assert old in s;s=s.replace(old,"source=verified_source(row);r=STEPControl_Reader();r.ReadFile(str(source));r.TransferRoots()")
 s='from project_paths import verified_source\n'+s;f.write_text(s,encoding='utf8',newline='\n')
# Adapt the verified corrected-reference campaign to a new finer mesh and its matching warm start.
s=(P/'v23_corrected_mesh_campaign.py').read_text(encoding='utf-8-sig');s=s.replace("O=P/'engineering-v23-results'","O=P/'engineering-v24-results'").replace('for mesh_size in [2.3,1.9]:','for mesh_size in [1.5]:')
old="mesh=P/'engineering-v21-results/refinement'/f'{size}_h1.9_mesh.npz' if mesh_size==1.9 else P/'engineering-v19-results/quadratic-contact'/f'{size}_h2.3.npz'"
new="""mesh=O/f'{size}_h{mesh_size}_mesh.npz'
  if not mesh.exists():
   cad,meshes=a.mesh(size,mesh_size,conforming=2,order=2,optimize_high_order=True)
   nodes=sum(len(x) for x,t in meshes)
   (O/f'{size}_mesh_trial.json').write_text(json.dumps(dict(nodes=nodes,mesh_size_mm=mesh_size,source_CAD_sha256=cad['sha256'],scope='New mesh on unchanged isolated V19 joint'),indent=2))
   assert nodes<85000, 'Resource guard; no equilibrium pass'
   np.savez_compressed(mesh,xt=meshes[0][0],tt=meshes[0][1],xf=meshes[1][0],tf=meshes[1][1]);print('New mesh',size,nodes,flush=True)"""
assert old in s;s=s.replace(old,new)
old="ref=P/'engineering-v21-results/refinement'/f'{size}_{side}_h1.9.npz' if mesh_size==1.9 else P/'engineering-v19-results'/('quadratic-contact' if side=='outward' else 'quadratic-inward')/f'{size}_h2.3.npz'"
new="ref=P/'engineering-v23-results'/f'{size}_h1.9_{side}.npz'";assert old in s;s=s.replace(old,new)
s=s.replace("z=np.load(ref);u=z['u'].copy();F=", "z=np.load(ref);from scipy.spatial import cKDTree\n   oldsplit=3*len(z['xt']);u=np.r_[z['u'][:oldsplit].reshape(-1,3)[cKDTree(z['xt']).query(m['xt'])[1]].ravel(),z['u'][oldsplit:].reshape(-1,3)[cKDTree(z['xf']).query(m['xf'])[1]].ravel()];u[m['fixed']]=0;F=")
s=s.replace('All eight corrected reference cases complete','All four finer corrected reference cases complete')
s=s.replace("assert np.allclose(F,z['force'],atol=1e-10)","assert np.allclose(F.reshape(-1,3).sum(axis=0),z['force'].reshape(-1,3).sum(axis=0),atol=1e-8)")
if not (P/'v24_finer_campaign.py').exists():(P/'v24_finer_campaign.py').write_text(s,encoding='utf8',newline='\n')
