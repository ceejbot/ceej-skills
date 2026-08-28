# ENOTIME

A small cross-host plugin that draws one of Brian Eno & Peter Schmidt's
[Oblique Strategies](https://en.wikipedia.org/wiki/Oblique_Strategies),
courtesy of the [`oblique`](https://github.com/ceejbot/oblique) CLI. Draw one
on demand with `$enotime:oblique-strategy` in Codex or `/oblique-strategy` in
Claude Code. Claude Code also draws one automatically at session start.

## Prerequisite

Install the `oblique` command-line tool:

```
brew install ceejbot/tap/oblique
```

Or, with cargo:

```
cargo install oblique
```

If `oblique` isn't installed, the plugin does nothing beyond reminding you how to install it.

## Install in Codex

```
codex plugin marketplace add ceejbot/ceej-skills
codex plugin add enotime@ceej-skills
```

Then invoke `$enotime:oblique-strategy` whenever a lateral prompt would help.

## Install in Claude Code

```
/plugin marketplace add ceejbot/ceej-skills
/plugin install enotime@ceej-skills
```

Then restart Claude Code. Honour thy error as a hidden intention.
