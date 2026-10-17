from pathlib import Path
import json,zipfile,hashlib
P=Path(__file__).parent;O=P/'engineering-v9-results';v=json.loads((O/'native_verification.json').read_text())
archives=[]
for n in v['files']:
    f=Path(n)
    if f.suffix!='.f3d':continue
    iszip=zipfile.is_zipfile(f)
    bad=None;methods=[];integrity='not checked'
    if iszip:
        with zipfile.ZipFile(f) as z:
            count=len(z.namelist());methods=sorted(set(i.compress_type for i in z.infolist()))
            try:bad=z.testzip();integrity='pass' if bad is None else 'fail'
            except NotImplementedError:integrity='unverified compression method unsupported by bundled Python'
    else:bad='Archive is not ZIP';count=0
    archives.append({'file':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size,'ZIP_members':count,'compression_methods':methods,'container_directory_readable':iszip and count>0,'member_integrity':integrity,'note':'Not a native reopening or feature-tree test.'})
poses=[]
for s in v['sizes']:
    rows=[r for r in v['STEP_checks'] if '_'+s['name']+'_' in Path(r['file']).name]
    vols=[r['volume_mm3'] for r in rows]
    delta=max(vols)-min(vols)
    poses.append({'size':s['name'],'STEP_count':len(rows),'volume_range_mm3':delta,'pass':len(rows)==3 and delta<.01,'note':'Rigid repositioning should preserve assembly volume; this does not test worn fit.'})
j={'status':'complete inventory' if len(archives)==6 and len(poses)==6 else 'partial','archives':archives,'pose_volume_checks':poses,'all_pose_volumes_pass':all(r['pass'] for r in poses),'all_archive_members_verified':all(r['member_integrity']=='pass' for r in archives)}
(O/'export_audit.json').write_text(json.dumps(j,indent=2));print(json.dumps({'status':j['status'],'archives':len(archives),'pose_sets':len(poses),'poses_pass':j['all_pose_volumes_pass'],'archive_integrity_verified':j['all_archive_members_verified']}))
