#!/bin/sh
# Emit hook JSON output: systemMessage is displayed directly to the user by
# Claude Code, so delivery does not depend on the model choosing to relay it.
escape() { printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g'; }

if command -v oblique >/dev/null 2>&1; then
  strategy=$(escape "$(oblique)")
  printf '{"systemMessage":"Oblique strategy for this session: %s","hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"This session'"'"'s Oblique Strategy, already shown to the user: %s. Let it inform your approach; no need to repeat it."}}\n' "$strategy" "$strategy"
else
  printf '{"systemMessage":"ENOTIME: the oblique CLI is not installed. Install it with: brew install ceejbot/tap/oblique  (or: cargo install oblique)"}\n'
fi
exit 0
