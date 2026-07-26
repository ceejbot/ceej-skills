# enotime

A tiny Claude Code plugin that draws one of Brian Eno & Peter Schmidt's [Oblique Strategies](https://en.wikipedia.org/wiki/Oblique_Strategies) at the start of every session, courtesy of the [`oblique`](https://github.com/ceejbot/oblique) CLI. You can also draw one on demand with `/oblique-strategy`.

## Prerequisite

Install the `oblique` command-line tool:

```
brew install ceejbot/tap/oblique
```

Or, with cargo:

```
cargo install --git https://github.com/ceejbot/oblique
```

If `oblique` isn't installed, the plugin does nothing beyond reminding you how to install it.

## Install

```
/plugin marketplace add ceejbot/ceej-skills
/plugin install enotime@ceej-skills
```

Then restart Claude Code. Honour thy error as a hidden intention.
