#!/bin/bash
# Launch offline NuToaster P0 dimension-play GUI on macOS.
# No software installation, network requests, or physical build commands.
set -eu
cd "$(dirname "$0")"
if command -v open >/dev/null 2>&1; then
  open "$(pwd)/tweak.html"
else
  echo "Open tweak.html manually in a browser."
fi
if command -v python3 >/dev/null 2>&1 && python3 -c 'import sys;sys.exit(0 if sys.version_info >= (3,10) else 1)'; then
  python3 "$(pwd)/generate.py" "$(pwd)/dist"
  echo "Provisional Minecraft and A3 files are in the dist folder."
else
  echo "Optional: Python 3.10+ is needed to generate Minecraft files; the slider editor works offline without it."
fi
