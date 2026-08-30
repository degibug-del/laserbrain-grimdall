#!/usr/bin/env bash
#
# Refresh the vendored copies from their upstream repos.
#
# Each directory here is a plain duplicate of one repository and is named after it. That is
# the whole rule. There is nothing to work out from a directory name.
#
#   laserbrain/         <- github.com/degibug-del/laserbrain
#   laserbrain-corpus/  <- github.com/degibug-del/laserbrain-corpus
#
# This replaced three git subtrees named sdk/, lasermind/ and lasergear/, which required a
# table to explain and did not survive the repos being renamed. Two of the three had also
# been folded into laserbrain itself by then, so the tree carried the same hooks twice under
# two different names.
#
# WHY THE EXACTNESS CHECK AT THE END. The same refresh in laserbrain-warden was done by hand
# twice and leaked build artifacts both times — __pycache__, .pytest_cache, egg-info,
# node_modules, and once a stale wheel. `git rm -r` removes tracked files only, and .gitignore
# hides those paths, so git never reports them and they survive every refresh invisibly. It
# also dropped files the other way: bare package.json patterns matched at any depth and the
# vendored TypeScript SDK shipped for nine days without the files needed to build it.
#
# So: the copy must equal upstream's tracked files exactly. Not a subset, not a superset.
#
set -euo pipefail
cd "$(dirname "$0")"

refresh() {
  local name="$1" src="$2"
  [ -d "$src/.git" ] || { echo "  no checkout at $src — skipping $name"; return 0; }

  if [ -n "$(git -C "$src" status --porcelain)" ]; then
    echo "  $src is dirty. Vendoring it would copy uncommitted state; commit first."
    return 1
  fi

  local sha n
  sha=$(git -C "$src" rev-parse --short HEAD)
  n=$(git -C "$src" ls-files | wc -l | tr -d ' ')

  git rm -r -q "$name" 2>/dev/null || true
  find "$name" -mindepth 1 -delete 2>/dev/null || true
  rmdir "$name" 2>/dev/null || true
  mkdir -p "$name"
  git -C "$src" archive HEAD | tar -x -C "$name"
  git add -A "$name"

  local disk tracked extra missing
# `-type f -o -type l` because research/ symlinks six files to javascript/ so the
# protocol exists once. `-type f` alone misses them and reports the vendor as short.
  disk=$(find "$name" \( -type f -o -type l \) | sed "s|^$name/||" | sort)
  tracked=$(git -C "$src" ls-files | sort)
  extra=$(comm -23 <(printf '%s\n' "$disk") <(printf '%s\n' "$tracked") || true)
  missing=$(comm -13 <(printf '%s\n' "$disk") <(printf '%s\n' "$tracked") || true)

  if [ -n "$extra" ] || [ -n "$missing" ]; then
    echo "  $name/ IS NOT AN EXACT COPY"
    [ -n "$extra" ]   && { echo "    leaked in:"; printf '%s\n' "$extra"   | sed 's/^/      /'; }
    [ -n "$missing" ] && { echo "    dropped:";   printf '%s\n' "$missing" | sed 's/^/      /'; }
    return 1
  fi
  echo "  ok  $name/ <- $sha, $n files, exact"
}

refresh laserbrain        "${LASERBRAIN_SRC:-$HOME/laserbrain}"
refresh laserbrain-corpus "${LASERBRAIN_CORPUS_SRC:-$HOME/laserbrain-corpus}"
