#!/usr/bin/env bash
# Fetch the source for every target, each pinned to its vulnerable version.
# Source is for reading. The live warm-up app comes from Docker (see targets/).
#   bash scripts/fetch_targets.sh
set -euo pipefail
cd "$(dirname "$0")/.."
SRC=targets/src
mkdir -p "$SRC"

clone_at() {  # repo  ref  dir
  local repo="$1" ref="$2"
  local dir="$SRC/$3"
  if [ -d "$dir/.git" ]; then echo "[skip] $3 already fetched"; return; fi
  echo "[fetch] $3 at $ref"
  git clone -q --filter=blob:none "$repo" "$dir"
  git -C "$dir" checkout -q "$ref"
}

plugin_zip() {  # slug  version
  local slug="$1" ver="$2"
  local dir="$SRC/$slug"
  if [ -d "$dir" ]; then echo "[skip] $slug already fetched"; return; fi
  echo "[fetch] $slug $ver (WordPress plugin)"
  local zip
  zip="$(mktemp -t "$slug").zip"
  curl -sL -o "$zip" "https://downloads.wordpress.org/plugin/${slug}.${ver}.zip"
  mkdir -p "$dir"; unzip -q -o "$zip" -d "$dir"; rm -f "$zip"
}

plugin_zip wp-polls              2.77.2
plugin_zip paid-member-subscriptions 2.15.1
plugin_zip woo-product-filter    2.9.7
plugin_zip wpdirectorykit        1.3.0
# Fork CMS has no plugin zip; clone the standalone CMS at the commit before the fix.
clone_at https://github.com/forkcms/forkcms 5.11.0 forkcms

echo
echo "Done. Source trees are under $SRC/."
echo "The live warm-up apps are the toy app and one WordPress target; see targets/README.md."
