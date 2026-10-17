"""Check publication hashes, required product assets, links and obvious credential patterns."""
from pathlib import Path
import hashlib,json,re,sys,urllib.parse,ast,zipfile
E=Path(__file__).resolve().parents[1];R=E.parents[1];m=json.loads((E/'publication_manifest.json').read_text());errors=[]
for r in m['records']:
 f=R/r['path']
 if not f.is_file() or hashlib.sha256(f.read_bytes()).hexdigest()!=r['published_sha256']:errors.append('Manifest mismatch: '+r['path'])
for f in R.rglob('*'):
 if not f.is_file() or any(p in f.relative_to(R).parts for p in ['.git','.workspaces']):continue
 if f.stat().st_size>=95_000_000:errors.append('Oversized file: '+str(f.relative_to(R)))
 if f.suffix=='.py':
  try:ast.parse(f.read_text(encoding='utf-8-sig'))
  except (SyntaxError,UnicodeDecodeError) as e:errors.append('Python parse: '+str(f.relative_to(R))+' '+str(e))
 if f.suffix in ['.py','.json','.md','.log','.txt','.csv']:
  try:t=f.read_text(encoding='utf-8-sig')
  except UnicodeDecodeError:continue
  # Patterns are assembled so this checker does not match its own source.
  if re.search('gh'+'p_[A-Za-z0-9]{30,}|github_'+'pat_[A-Za-z0-9_]{30,}|sk'+'-[A-Za-z0-9]{35,}',t):errors.append('Possible credential: '+str(f.relative_to(R)))
for f in [R/'README.md',R/'CONTRIBUTING.md',R/'SoftSpace/README.md',R/'SoftSpace Flex/README.md',E/'README.md']:
 t=f.read_text(encoding='utf-8')
 links=re.findall(r'\]\(([^)]+)\)|(?:href|src)="([^"]+)"',t)
 for pair in links:
  link=next(x for x in pair if x);link=urllib.parse.unquote(link.split('#')[0])
  if not link or re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:',link):continue
  if not (f.parent/link).exists():errors.append('Broken link in '+str(f.relative_to(R))+': '+link)
for name in ['SoftSpace/reports/SoftSpace_Report.docx','SoftSpace Flex/reports/SoftSpace_Flex_Report.docx']:
 with zipfile.ZipFile(R/name) as z:
  if z.testzip() is not None:errors.append('DOCX integrity: '+name)
for folder in ['quadratic-contact','quadratic-inward']:
 v=json.loads((E/'evidence/engineering-v19-results'/folder/'verification.json').read_text())
 if len(v['array_audits'])!=4 or any(r['status']!='pass' for r in v['array_audits']):errors.append('Unexpected recorded audits: '+folder)
print(json.dumps(dict(manifest_files=len(m['records']),errors=errors,status='pass' if not errors else 'fail'),indent=2));sys.exit(bool(errors))
