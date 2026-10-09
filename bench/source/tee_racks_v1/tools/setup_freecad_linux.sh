#!/usr/bin/env bash
# Pinned official local runtime; cache excluded from Git. No system package changes.
set -euo pipefail
repo_root=$(cd "$(dirname "$0")/../../../.." && pwd)
runtime_dir="$repo_root/.local-runtime/freecad-1.1.3"
mkdir -p "$runtime_dir"
cd "$runtime_dir"
if [[ ! -f FreeCAD.AppImage ]]; then
  curl -fL --retry 2 --connect-timeout 15 --max-time 600 \
    https://github.com/FreeCAD/FreeCAD/releases/download/1.1.3/FreeCAD_1.1.3-Linux-x86_64-py311.AppImage -o FreeCAD.AppImage
fi
printf '%s  %s\n' '3a853eb69ee595f779f2255dbf80a765926981d8ff68903cefee4dfb03a8f5ef' 'FreeCAD.AppImage' | sha256sum -c -
chmod +x FreeCAD.AppImage
if [[ ! -f squashfs-root/AppRun ]]; then
  timeout 180 ./FreeCAD.AppImage --appimage-extract > extract.log 2>&1
fi
cat > "$repo_root/.local-runtime/freecad-python" <<'WRAPPER'
#!/usr/bin/env bash
set -euo pipefail
runtime_dir=$(cd "$(dirname "$0")/freecad-1.1.3/squashfs-root" && pwd)
export PYTHONPATH="$runtime_dir/usr/lib${PYTHONPATH:+:$PYTHONPATH}"
exec "$runtime_dir/AppRun" python "$@"
WRAPPER
chmod +x "$repo_root/.local-runtime/freecad-python"
cd "$repo_root"
timeout 30 .local-runtime/freecad-python -c 'import FreeCAD, Part, scipy; print("FreeCAD", FreeCAD.Version()[:3], "OCC", Part.OCC_VERSION, "scipy", scipy.__version__)'
