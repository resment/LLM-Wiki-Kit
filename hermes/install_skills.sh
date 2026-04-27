#!/usr/bin/env sh
set -eu

TARGET="${1:-$HOME/.hermes/skills/llm-wiki-kit}"
SOURCE_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)/skills"

mkdir -p "$TARGET"

for skill in "$SOURCE_DIR"/*; do
  [ -d "$skill" ] || continue
  name="$(basename "$skill")"
  dest="$TARGET/$name"
  if [ -e "$dest" ]; then
    echo "skip $dest"
    continue
  fi
  cp -R "$skill" "$dest"
  echo "copy $dest"
done
