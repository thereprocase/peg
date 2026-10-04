"""Package checked current-mount exports; uploads and Git publication are separate.

python publication/build_current_pegs.py BUILD_DIR RELEASE_DIR
Each product has a report.json, checked native exports and preview media.
"""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / 'docs/gallery/current-pegs'
SOURCE = ROOT / 'bench/source/gallery_current_mounts_v1'
TAG = 'current-pegs-v1-2026-10-04'
BASE = f'https://github.com/thereprocase/peg/releases/download/{TAG}/'


def digest(path):
    data = path.read_bytes()
    return {'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}


def main(build, release, selected=None, tag=TAG, selection=None, generation_source_map=None):
    base = f'https://github.com/thereprocase/peg/releases/download/{tag}/'
    reports = [ROOT / row['report'] for row in json.loads(selection.read_text())['products']] if selection else sorted(build.glob('*/report.json'))
    if selected:
        reports = [p for p in reports if p.parent.name in selected]
    expected_count = len(selected) if selected else 38
    assert len(reports) == expected_count, len(reports)
    release.mkdir(parents=True, exist_ok=True)
    PAGE.mkdir(parents=True, exist_ok=True)
    moves_file = ROOT / 'publication/release-downloads.json'
    assets_file = ROOT / 'publication/release-assets.json'
    moves, assets = json.loads(moves_file.read_text()), json.loads(assets_file.read_text())
    additions, catalog, release_paths = {}, [], []
    generation_sources = {}
    if generation_source_map:
        generation_sources = {row['id']: row for row in json.loads(generation_source_map.read_text())['products']}
    for report_path in reports:
        info = json.loads(report_path.read_text())
        assert info['checks']['pass'], info['id']
        prefix = 'part-' + info['id'].lower() + '__' + info['version'] + '__fit-pf02c9-hoop5'
        folder = report_path.parent
        presentation = json.loads((folder / 'presentation.json').read_text())
        for role in ['installed', 'print']:
            assert presentation['input_stl_sha256'][role] == digest(folder / info['assets'][role + '_stl'])['sha256']
        export_assets = dict(info['assets'], **presentation['assets'])
        mapping = {}
        for role in ['installed_stl', 'print_stl', 'installed_glb', 'print_glb',
                     'installed_png', 'print_png', 'preview_png']:
            original = folder / export_assets[role]
            label = role.split('_')[0] if role != 'preview_png' else 'preview'
            if role == 'print_stl':
                label = 'print-' + info['pose']
            target = PAGE / (prefix + '__' + label + original.suffix)
            shutil.copy2(original, target)
            mapping[role] = target.name
            additions[target.name] = digest(target)
        check_file = PAGE / (prefix + '__checks.json')
        shutil.copy2(report_path, check_file)
        mapping['checks'] = check_file.name
        additions[check_file.name] = digest(check_file)
        native = []
        for role in ['installed_step', 'print_step']:
            original = folder / export_assets[role]
            label = 'print-' + info['pose'] if role == 'print_step' else 'installed'
            target = release / (prefix + '__' + label + '.step')
            shutil.copy2(original, target)
            native.append(target)
            mapping[role] = base + target.name
        bundle = release / (prefix + '__cad-source-and-review.zip')
        with zipfile.ZipFile(bundle, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
            z.write(ROOT / 'docs/gallery/pegstr/ATTRIBUTION.txt', 'ATTRIBUTION.txt')
            for p in sorted(SOURCE.rglob('*')):
                if p.is_file() and p.suffix in {'.py', '.json', '.scad', '.step', '.md', '.txt'}:
                    z.write(p, p.relative_to(ROOT).as_posix())
            input_file = Path(info['source']['input'])
            assert digest(input_file)['sha256'] == info['source']['input_sha256']
            input_name = 'inputs/original' + input_file.suffix.lower()
            z.write(input_file, input_name)
            spec = dict(info['source'], input=input_name)
            for ancestry in ['original_step', 'original_mesh']:
                if ancestry in spec:
                    original = Path(spec[ancestry])
                    assert digest(original)['sha256'] == spec[ancestry + '_sha256']
                    archived = 'inputs/' + ancestry.replace('_', '-') + original.suffix.lower()
                    z.write(original, archived)
                    spec[ancestry] = archived
            z.writestr('spec.json', json.dumps(spec, indent=2) + '\n')
            if generation_source_map:
                archived_sources = generation_sources[info['id']]['executed_authored_sources']
                for archived in archived_sources:
                    original = Path(archived['generation_source_path'])
                    assert digest(original)['sha256'] == archived['generation_source_sha256']
                    z.write(original, archived['bundle_path'])
                public_provenance = [{k: v for k, v in archived.items() if k != 'generation_source_path'} for archived in archived_sources]
                z.writestr('generation-sources/provenance.json', json.dumps(public_provenance, indent=2) + '\n')
            written_exports = set()
            for role, filename in export_assets.items():
                p = folder / filename
                if p.is_file() and p.name not in written_exports:
                    z.write(p, 'exports/' + p.name)
                    written_exports.add(p.name)
            z.write(report_path, 'exports/report.json')
            for evidence in ['native-checks.json', 'seat-checks.json', 'mesh-checks.json', 'presentation.json', 'NOTES.md']:
                if (folder / evidence).is_file() and evidence not in written_exports:
                    z.write(folder / evidence, 'exports/' + evidence)
            z.writestr('README.txt',
                      info['name'] + ' — ' + info['version'] + '\n\n'
                      'PF02 #9 top hooks and PF07 #5 bottom hoops, clipped roots.\n'
                      'Read exports/report.json for print orientation, geometry checks and limits.\n'
                      'No sliced job is included. Physical fit and loads remain untested.\n\n'
                      'Rebuild from the extracted bundle using FreeCAD Python with numpy:\n'
                      '  freecad-python bench/source/gallery_current_mounts_v1/' + ('flat_top_p06_export.py' if info['id'] == 'P06' else 'flat_top.py' if info['pose'] == 'inverted-flat-top' else 'remount.py') + ' spec.json rebuilt\n'
                      'Some retained source bodies are faceted STL-derived STEP, as declared in their history.\n'
                      'generation-sources/ preserves the exact execution sources and their hashes.\n'
                      'The packaged rebuild sources include documented AST-identical whitespace cleanup.\n'
                      'Original Pegstr derivatives: Marius Gheorghescu / mgx, CC Attribution–NonCommercial.\n'
                      'See https://thereprocase.github.io/peg/gallery/pegstr/ATTRIBUTION.txt\n')
        with zipfile.ZipFile(bundle) as z:
            assert z.testzip() is None, bundle.name
            assert hashlib.sha256(z.read(input_name)).hexdigest() == info['source']['input_sha256']
        native.append(bundle)
        mapping['cad_bundle'] = base + bundle.name
        for p in native:
            receipt = digest(p)
            moves['current-pegs/' + p.name] = base + p.name
            assets[p.name] = receipt
            additions[p.name] = receipt
            release_paths.append(p.name)
        # These notes are reviewed by root against each matching report before publishing.
        assert isinstance(presentation['public_notes'], dict), info['id']
        catalog.append({'id': info['id'], 'name': presentation.get('public_name', info['name']), 'family': {'bins':'bin-expansion','solder':'solder-modules'}.get(info['family'],info['family']),
                        'version': info['version'], 'fit_label': 'PF02 #9 / PF07 #5',
                        'pose': info['pose'], 'print_bounds_mm': info['print_bounds_mm'],
                        'assets': mapping, 'notes': presentation['public_notes'],
                        'credit': presentation.get('credit', '')})
    catalog_file = PAGE / 'catalog.json'
    catalog_file.write_text(json.dumps({'schema_version': 1, 'expected_count': expected_count,
                                       'parts': catalog,
                                       'build_note': ('P09-36 priority release · Flat top and current pegs · Other holders are being updated.' if selected else 'October 4, 2026 · Per-model CAD and print-orientation checks; physical testing pending.')}, indent=2) + '\n')
    for p in [catalog_file, PAGE / 'index.html', PAGE / 'current-pegs.js', PAGE / 'current-pegs.css']:
        additions[p.name] = digest(p)
    (ROOT / 'publication/current-pegs-v1-additions.json').write_text(json.dumps(additions, indent=2) + '\n')
    moves_file.write_text(json.dumps(moves, indent=2) + '\n')
    assets_file.write_text(json.dumps(assets, indent=2) + '\n')
    js_file = ROOT / 'docs/gallery/release-downloads.js'
    existing_js = js_file.read_text()
    before, old_map_tail = existing_js.split('const links=', 1)
    _, after = old_map_tail.split(';function fix(node)', 1)
    js_file.write_text(before + 'const links=' + json.dumps(moves, separators=(',', ':'))
                       + ';function fix(node)' + after)
    (release / 'release-files.json').write_text(json.dumps(release_paths, indent=2) + '\n')
    print(json.dumps({'parts': len(catalog), 'site_receipts': len(additions),
                      'release_files': len(release_paths), 'tag': tag}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('build', type=Path)
    parser.add_argument('release', type=Path)
    parser.add_argument('--select', nargs='+')
    parser.add_argument('--tag', default=TAG)
    parser.add_argument('--selection', type=Path)
    parser.add_argument('--generation-source-map', type=Path)
    args = parser.parse_args()
    main(args.build, args.release, args.select, args.tag, args.selection, args.generation_source_map)
