# list recipes
_help:
	just -l

# Install tools.
setup:
	#!/usr/bin/env bash
	brew tap ceejbot/tap
	brew install --quiet ceejbot/tap/semver-bump jq

# Tag a new plugin version for release. Run from the plugin directory.
version BUMP:
	#!/usr/bin/env bash
	set -euo pipefail
	cd {{ invocation_directory() }}
	PLUGIN_JSON=".claude-plugin/plugin.json"
	[ -f "$PLUGIN_JSON" ] || { echo "no $PLUGIN_JSON here; run from a plugin directory" >&2; exit 1; }
	[ -z "$(git status --porcelain -- .)" ] || { echo "commit or stash this plugin's changes first" >&2; exit 1; }
	read -r plugin current < <(jq -r '"\(.name) \(.version)"' "$PLUGIN_JSON")
	version=$(semver-bump {{BUMP}} "$current")

	echo "Preparing release v${version} for ${plugin}…"
	jq --tab --arg version "$version" '.version = $version' "$PLUGIN_JSON" > "$PLUGIN_JSON.tmp"
	mv "$PLUGIN_JSON.tmp" "$PLUGIN_JSON"
	git commit "$PLUGIN_JSON" -m "$plugin v$version"
	git push
	claude plugin tag --push
