#!/bin/sh
if command -v oblique >/dev/null 2>&1; then
  printf 'Oblique strategy for this session: "%s". Quote it to the user, verbatim, at the top of your first reply.\n' "$(oblique)"
else
  echo "enotime: the oblique CLI is not installed. Tell the user to run: brew install ceejbot/tap/oblique  (or: cargo install --git https://github.com/ceejbot/oblique)"
fi
exit 0
