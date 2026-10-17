"""Read-only binary STL closure, winding, connected-surface and bed checks."""
import collections
import hashlib
import json
from pathlib import Path
import struct
import sys


def check(path):
    raw=Path(path).read_bytes()
    count=struct.unpack_from('<I',raw,80)[0]
    assert len(raw)==84+50*count
    edges={};directions=collections.Counter();parent=list(range(count));volume=0;min_z=float('inf')
    def root(i):
        while parent[i]!=i:
            parent[i]=parent[parent[i]];i=parent[i]
        return i
    for i in range(count):
        coordinates=struct.unpack_from('<9f',raw,84+50*i+12)
        a,b,c=[tuple(coordinates[j*3:j*3+3]) for j in range(3)]
        min_z=min(min_z,a[2],b[2],c[2])
        volume+=(a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6
        for x,y in [(a,b),(b,c),(c,a)]:
            assert x!=y, 'collapsed triangle'
            edge=tuple(sorted((x,y)))
            directions[edge]+=1 if x<y else -1
            edges.setdefault(edge,[]).append(i)
    assert all(len(faces)==2 for faces in edges.values()), 'open/nonmanifold edge'
    assert all(x==0 for x in directions.values()), 'inconsistent winding'
    for a,b in edges.values():parent[root(a)]=root(b)
    components=len({root(i) for i in range(count)})
    assert components==1 and volume>0 and min_z>=-1e-5
    return dict(triangles=count,edges=len(edges),connected_surfaces=components,
                volume_mm3=volume,minimum_z_mm=min_z,closed=True,consistent_winding=True,
                sha256=hashlib.sha256(raw).hexdigest())

if __name__=='__main__':
    print(json.dumps(check(sys.argv[1]),indent=2))
