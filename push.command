#!/bin/bash
# Tough Country Fitness - commit and push composites and ledger.
# Double click this file. It runs in Terminal and closes itself out.

cd "$(dirname "$0")" || exit 1

echo "Tough Country Fitness sync"
echo "=========================="
echo

# git leaves this behind when a session writes to the repo without being able
# to clean up after itself. Harmless to remove; blocks everything if left.
rm -f .git/index.lock

if [ -z "$(git status --porcelain)" ]; then
  echo "Nothing new to commit."
else
  git add -A
  git commit -m "TCF sync $(date '+%Y-%m-%d %H:%M')"
  echo
fi

echo "Pushing..."
if git push; then
  echo
  echo "Done. Everything is on GitHub."
else
  echo
  echo "Push failed. Screenshot this window and send it to Claude."
fi

echo
echo "You can close this window."
