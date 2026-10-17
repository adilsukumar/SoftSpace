from pathlib import Path
import sys,json,platform
P=Path(__file__).parent;sys.path.insert(0,str(P/'solver-libraries'))
import numpy,scipy,gmsh,matplotlib
r={'python':sys.version,'python_executable':sys.executable,'platform':platform.platform(),'numpy':numpy.__version__,'scipy':scipy.__version__,'gmsh':gmsh.__version__,'matplotlib':matplotlib.__version__,'scope':'Versions available to the final recorded checks. Earlier numerical rows retain their own recorded method fields; this is not a retroactive binary provenance certificate.','timing_note':'The seconds fields use elapsed wall-clock time. Scheduling pauses or laptop suspension can be included; they are not CPU benchmarks.','dependencies_note':'Solver libraries are present in the local project; the results ZIP does not bundle those library installations.'}
(P/'engineering-v10-results'/'runtime_versions.json').write_text(json.dumps(r,indent=2));print(json.dumps(r))
