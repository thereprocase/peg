"""Check current-mount publication receipts and dynamic catalog asset links."""
from pathlib import Path
from urllib.parse import unquote, urlsplit
import hashlib
import json
import math

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / 'docs/gallery/current-pegs'


def main():
    catalog = json.loads((PAGE / 'catalog.json').read_text())
    additions = json.loads((ROOT / 'publication/current-pegs-v1-additions.json').read_text())
    moves = json.loads((ROOT / 'publication/release-downloads.json').read_text())
    assets = json.loads((ROOT / 'publication/release-assets.json').read_text())
    seen = set()
    count = 0
    for part in catalog['parts']:
        assert part['id'] not in seen, part['id']
        seen.add(part['id'])
        assert part['pose'] in {'upright', 'right-cheek', 'left-cheek', 'flat-top', 'inverted-flat-top', 'vase'}, part['id']
        assert len(part['print_bounds_mm']) == 3
        assert all(math.isfinite(float(n)) and n > 0 for n in part['print_bounds_mm'])
        assert part['fit_label'] == ('Removable accessory · no pegs' if part.get('kind') == 'accessory' else 'PF02 #9 / PF07 #5'), part['id']
        for note in ['orientation', 'upper_pegs', 'supports', 'mount', 'qualification']:
            assert part['notes'][note].strip(), (part['id'], note)
        assert 'physical' in part['notes']['qualification'].lower(), part['id']
        for role in ['installed_glb', 'print_glb', 'preview_png', 'print_stl',
                     'installed_stl', 'cad_bundle', 'checks'] + ([role for role in ['installed_step', 'print_step'] if role in part['assets']]):
            address = part['assets'][role]
            parsed = urlsplit(address)
            if parsed.scheme:
                assert address.startswith('https://github.com/thereprocase/peg/releases/download/'), address
                assert any(tag in address for tag in ['current-pegs-v1-2026-10-04/', 'p09-36-current-pegs-v1-2026-10-04/', 'p09-36-flat-top-v2-2026-10-04/', 'current-pegs-v2-2026-10-04/', 'new-designs-v1-2026-10-04/', 'cascade-funnels-v2-2026-10-06/', 'cascade-funnels-v3-2026-10-06/', 'canted-hex-keys-v1-2026-10-06/', 'canted-hex-keys-v2-2026-10-07/', 'key-fan-v1-2026-10-08/', 'key-fan-v2-2026-10-08/']), address
                name = unquote(parsed.path.rsplit('/', 1)[-1])
                assert name in assets, name
                assert address in moves.values(), address
            else:
                target = PAGE / unquote(parsed.path)
                assert target.resolve().is_relative_to(PAGE.resolve()), address
                assert target.is_file(), address
                assert target.name in additions, address
            assert not address.endswith(('.gcode', '.3mf')), address
            count += 1
    assert len(seen) == catalog['expected_count'], (len(seen), catalog['expected_count'])
    for name, metadata in additions.items():
        path = PAGE / name
        if path.is_file():
            actual = path.read_bytes()
            assert hashlib.sha256(actual).hexdigest() == metadata['sha256'], name
            assert len(actual) == metadata.get('bytes', metadata.get('size')), name
        else:
            key = 'current-pegs/' + name
            assert key in moves, key
            assert assets[moves[key].rsplit('/', 1)[-1]] == metadata, name
    print(json.dumps({'current_parts': len(seen), 'catalog_assets': count,
                      'receipts': len(additions), 'errors': []}, indent=2))


if __name__ == '__main__':
    main()
