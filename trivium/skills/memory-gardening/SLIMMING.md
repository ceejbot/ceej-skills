# Slimming a hot memory

Reached from `memory-gardening` when `stats.py` reports a **hot** memory over
the cap. The vocabulary — hot, cold, the cap, retiring — is defined in
`../../TAXONOMY.md`, *Weight: hot and cold*. Slimming uses `memorize` only,
so it needs no merge and no archive decision: `export-0` is the undo for
every step.

A pass whose stats show full alias and link coverage, no near-duplicates,
and one or two memories over the cap is a **weight pass**: run steps 1 and 2
of the skill, this file, then steps 9 and 10.

## Steps

### 1. Sort the hot body on disk

Read the over-cap memory from the export. Assign every paragraph one home
from the taxonomy's table: state stays; a ruling becomes one ledger line;
evidence goes to a log; a working list gets its own spoke; shipped
follow-ups go to history. Write one file per destination in
`<scratch>/ops/`.

Build the cold files by script from the export, so the text is verbatim.
Write the slim hot body by hand: it is the one file that takes judgment.

Done when every paragraph of the old body appears in exactly one cold file
or is restated in the slim body.

### 2. Check every claim the text carries

Retiring is the one time every line is read. For each quoted phrase, grep
the source for the quote. For each "open" or "still to apply" item, check
whether it has been done. For each hash, `git cat-file -t <hash>`.

Correct the cold file where the source disagrees, and say so in the file:
the old wording, the wording on the page, the date. On the 2026-09 forsyte
pass two quotes and two "open" items in a 32k focus were already stale.

Done when every quote, hash, and open item in the new files has been checked
once against its source.

### 3. Write the cold memories, then verify them

`memorize` each cold file under a new mnemonic with its full tag set. Choose
mnemonics that read differently from the hot memory's and from each other's:
a new mnemonic within distance 0.15 of an existing one is auto-merged into
it, and the response is the only notice.

The `trivia` CLI writes a file's text exactly:

```
trivia memorize -t project:<slug> -t learned -t theme:<theme> \
    "<mnemonic>" "$(cat <scratch>/ops/<file>)"
```

Verify each with a tag-filtered recall: the mnemonic matches, the tags are
the ones passed, the length is the file's length.

Done when every cold memory passes that check.

### 4. Slim the hot memory

`memorize` the slim body onto the hot mnemonic with its full tag set. For a
focus, GROUND TRUTH gains one pointer per cold memory — `<mnemonic> — load
when <task>` — and FOLLOW-UPS gains one line naming the history memory that
holds the retired tombstones.

Archive the old hot body whole: `memorize` it verbatim as
`<slug>/history/<yyyy-mm>-<arc>` with tags `["project:<slug>", "archive"]`.
The cold files may condense; this copy does not.

Done when a tag-filtered recall shows the hot memory under the cap with its
tags intact, and a fresh export contains every paragraph of the old body.
Check the second with a script over `export-0` and the fresh export: split
the old body on blank lines and search for each paragraph.

### 5. Give the cold memories their findability

Each cold spoke gets one or two aliases, a link to its theme hub, and a
place on a hub line — usually as a citation on the line whose rule it
serves. The hub line that named the hot memory now names its cold stores
and says when each is loaded.

Then amend every other layer that names the hot memory: `<slug>/conventions`,
the project's `CLAUDE.md` or `AGENTS.md`, and any project skill that recalls
it. A skill that recalls the memory by an old alias keeps working by
accident; give it the exact mnemonic.

Done when `grep -rn "<hot mnemonic's handle>"` over the project's agent
documents returns only lines that match the new arrangement.

### 6. Probe

Ask three questions a later session would ask, worded differently from the
aliases, each with `full_text_search` on a distinctive body word. Each
returns the memory that now holds the answer in its top three. A miss gets
one sharper alias and a rerun.
