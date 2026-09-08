"""Hash the intended git-tracked release. Stage new files before running."""
from pathlib import Path
import hashlib,json,subprocess
root=Path(__file__).resolve().parent
paths=subprocess.check_output(['git','ls-files','-z'],cwd=root).decode().rstrip('\0').split('\0')
files=[]
for name in sorted(set(paths)):
    p=root/name
    if name=='release_manifest.json' or not p.is_file():continue
    data=p.read_bytes()
    files.append({'path':name,'size_bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
manifest={'schema_version':1,'project':'thereprocase/peg','scope':'All intended tracked release files, excluding this manifest, Git metadata, caches, and review-only G-code. Current round files and labeled rectangular baseline are both preserved.','hash_algorithm':'SHA-256','file_count':len(files),'total_size_bytes':sum(f['size_bytes'] for f in files),'files':files}
(root/'release_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(f"{len(files)} files; {manifest['total_size_bytes']} bytes")
