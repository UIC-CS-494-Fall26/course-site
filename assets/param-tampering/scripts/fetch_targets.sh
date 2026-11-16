#!/usr/bin/env bash
# Fetch the source for every target, each pinned to its vulnerable commit.
# Source is for reading. The running apps come from Docker (see targets/).
#   bash scripts/fetch_targets.sh
set -euo pipefail
cd "$(dirname "$0")/.."
SRC=targets/src
mkdir -p "$SRC"

clone_at() {  # repo  ref  dir
  local repo="$1" ref="$2" dir="$SRC/$3"
  if [ -d "$dir/.git" ]; then echo "[skip] $3 already fetched"; return; fi
  echo "[fetch] $3 at $ref"
  git clone -q --filter=blob:none "$repo" "$dir"
  git -C "$dir" checkout -q "$ref"
}

plugin_zip() {  # slug  version
  local slug="$1" ver="$2" dir="$SRC/$slug"
  if [ -d "$dir" ]; then echo "[skip] $slug already fetched"; return; fi
  echo "[fetch] $slug $ver (WordPress plugin)"
  local zip; zip="$(mktemp -t "$slug").zip"
  curl -sL -o "$zip" "https://downloads.wordpress.org/plugin/${slug}.${ver}.zip"
  mkdir -p "$dir"; unzip -q -o "$zip" -d "$dir"; rm -f "$zip"
}

clone_at https://github.com/kanboard/kanboard            v1.2.50       kanboard
clone_at https://github.com/rconfig/rconfig              core-8.2.7    rconfig
# Shopizer has no 2.x git tag; pin the commit before the fix (929ca08^1).
clone_at https://github.com/shopizer-ecommerce/shopizer  de8a8e3183f8c5fed4695f889e309a6fff70adae  shopizer
# Microweber git stops at v1.3.4; pin the commit before the fix (890e983^).
clone_at https://github.com/microweber/microweber        5eb9c331b443a6e0bb30540bbc11c4989946a512  microweber
plugin_zip ninja-forms            3.14.8
plugin_zip wp-time-slots-booking-form 1.2.06

echo
echo "Done. Source trees are under $SRC/."
echo "The two apps that run in one container are the toy shop and Kanboard;"
echo "see targets/README.md."
