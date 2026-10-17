from pathlib import Path
from zipfile import ZipFile
p=Path(__file__).parent
with ZipFile(next((p/'solver-wheel').glob('gmsh*.whl'))) as z:
    candidates=[n for n in z.namelist() if n.endswith('gmsh-4.13.dll')]
    assert len(candidates)==1,candidates
    target=p/'solver-libraries'/'gmsh-4.13.dll'
    target.write_bytes(z.read(candidates[0]))
    print('Extracted',target,target.stat().st_size)
