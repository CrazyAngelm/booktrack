#!/bin/bash

# Check if both parameters are provided
if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <commit-hash> <HH:MM:SS>"
  exit 1
fi

COMMIT_HASH="$1"
TIME="$2"
FIXED_DATE="2025-05-09T$TIME"

# Change commit date using git filter-branch
git filter-branch -f --env-filter "
if [ \"\$GIT_COMMIT\" = \"$COMMIT_HASH\" ]; then
    export GIT_AUTHOR_DATE=\"$FIXED_DATE\"
    export GIT_COMMITTER_DATE=\"$FIXED_DATE\"
fi
" -- --all

# Remove backup refs created by filter-branch
git for-each-ref --format="%(refname)" refs/original/ | while read ref; do
  git update-ref -d \"$ref\"
done

# Clean up reflog and run garbage collection
git reflog expire --expire=now --all
git gc --prune=now --aggressive

echo "Commit $COMMIT_HASH date updated to $FIXED_DATE."