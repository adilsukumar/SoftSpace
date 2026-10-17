from pathlib import Path
import json, subprocess, sys, os
P=Path(__file__).parent
env=dict(os.environ, OPENBLAS_NUM_THREADS='1')
for size in ['child_small','child_medium','child_large','adult_medium','adult_large']:
    for h in [2.0,1.5,1.25,1.0]:
        f=P/'engineering-v9-results'/(size+'_h'+str(h)+'.json')
        if not f.exists():
            subprocess.run([sys.executable,str(P/'solid_band_v9.py'),size,str(h)],cwd=P,env=env,check=True)
        if h<2:
            a=json.loads((P/'engineering-v9-results'/(size+'_h'+str({1.5:2.0,1.25:1.5,1.0:1.25}[h])+'.json')).read_text())
            b=json.loads(f.read_text())
            ds=abs(b['max_von_mises_centroid_MPa']/a['max_von_mises_centroid_MPa']-1)
            du=abs(b['guide_mean_x_displacement_mm']/a['guide_mean_x_displacement_mm']-1)
            print(json.dumps({'size':size,'mesh':h,'stress_change':ds,'guide_change':du}),flush=True)
            if ds<.05 and du<.05:break
subprocess.run([sys.executable,str(P/'summarize_native_v9.py')],cwd=P,env=env,check=True)
