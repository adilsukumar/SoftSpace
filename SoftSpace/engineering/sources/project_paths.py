"""Resolve saved project provenance paths after relocation, retaining hash checks."""
from pathlib import Path
import hashlib
ROOT=Path(__file__).resolve().parent

def verified_source(row):
 raw=str(row['file']).replace('\\','/');candidates=[Path(raw.replace('${WORKSPACE}',ROOT.as_posix()))]
 marker='/EarDefenderProject/'
 if marker in raw:candidates.append(ROOT/raw.split(marker,1)[1])
 candidates.append(ROOT/Path(raw).name)
 candidates.append(ROOT/'source-archive'/row['sha256']/Path(raw).name)
 for p in candidates:
  if p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']:return p
 raise FileNotFoundError('No saved source matches recorded hash: '+raw)
