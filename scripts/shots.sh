#!/usr/bin/env bash
# Regenerate the OG card, the favicon, and page/book screenshots.
# Renders HTML with headless Chrome. macOS paths; adjust CHROME for other OSes.
#
# Usage:
#   ./scripts/shots.sh            # render og.png + icon.png from local HTML
#   ./scripts/shots.sh <url>      # also screenshot a live URL (page + book)
set -euo pipefail

CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/screenshots"
mkdir -p "$OUT"

# Chrome's new headless doesn't exit after --screenshot, so we background it,
# give it a moment to write the file, then kill that one instance.
shot() { # name  WxH  url
  local ud; ud="$(mktemp -d)"
  "$CHROME" --headless=new --disable-gpu --no-sandbox --no-first-run \
    --user-data-dir="$ud" --hide-scrollbars --force-device-scale-factor=2 \
    --window-size="$2" --virtual-time-budget=6000 --screenshot="$1" "$3" \
    >/dev/null 2>&1 &
  perl -e 'select(undef,undef,undef,9)'   # wait ~9s (no `sleep` dependency)
  pkill -f "$ud" 2>/dev/null || true
  rm -rf "$ud"
  [ -f "$1" ] && echo "  wrote $1" || echo "  FAILED $1"
}

echo "Rendering OG card + favicon..."
shot "$ROOT/og.png"   "1200,630" "file://$ROOT/og.html"
shot "$ROOT/icon.png" "512,512"  "file://$ROOT/icon.html"

URL="${1:-}"
if [ -n "$URL" ]; then
  BASE="$URL/?theme=light&still=1"
  echo "Screenshotting $URL ..."
  shot "$OUT/hero.png"     "1440,940"  "$BASE"
  shot "$OUT/overview.png" "1440,3600" "$BASE"
  shot "$OUT/book.png"     "1440,940"  "$BASE#book"
fi

pkill -f "Google Chrome.*--headless" 2>/dev/null || true
echo "Done. Output in $OUT (screenshots) and repo root (og.png, icon.png)."
