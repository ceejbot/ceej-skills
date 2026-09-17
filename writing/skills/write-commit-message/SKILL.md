---
name: write-commit-message
description: Use before running `git commit`, `gh pr create`, or `gh pr edit`, and when asked to draft a commit message or PR description. In squash-merge repos the PR title and body become the trunk commit, so a PR description is a commit message. A fixup commit the author will autosquash needs only a headline.
---

# Writing Commit Messages

In a squash-merge repo the PR title becomes the headline and the PR body becomes
the message of the commit that lands on trunk. A PR description is therefore a
commit message, and this skill covers both. The reader is a maintainer years
from now, often you with no memory of the work, staring at one `git blame` line
and asking why the code is the way it is.

**Core principle:** trunk commits are the durable record. They outlive the PR,
the issue tracker, and the hosting provider. Write the message that reader
needs, at the length the change earns, and nothing more.

## When to use

- Before `git commit` on work that will reach trunk.
- Before `gh pr create` or `gh pr edit`: the PR title and body are the commit.
- When asked to draft a commit message or PR description.

A fixup commit the author will autosquash needs only a headline.

## Steps

### 1. Read the diff

`git diff <range>` or `git log <range>`. The diff is ground truth; conversation
memory is not. Note what a reader could not learn from the diff alone: the
problem that prompted the change, the alternative not taken, the thing left
deliberately undone. Done when you can say why the change exists in one
sentence.

### 2. Write the headline

Imperative mood, about 50 characters, a Conventional Commits prefix (`feat:`,
`fix:`, `docs:`, `chore:`) with an optional scope. Issue numbers go on the last
line of the body, where they cost no headline characters. The headline is the
hardest line; let it shape the rest.

### 3. Write the lede

One paragraph: what was happening, what it caused, and what the change does
about it. How does the system behave now that it did not before, and why? Done
when a reader who stops here has the gist.

### 4. Decide whether the change earns more

A config tweak or a routine fix is finished at the lede. Add a paragraph only
for something the lede could not hold: a non-obvious technical choice, a viable
alternative rejected and why, a deliberate omission, a drive-by fix in adjacent
code. A subtle concurrency fix can run to ten paragraphs; most changes run to
one or two. Done when every paragraph tells the reader something the diff
cannot.

### 5. Add references last

`Closes #NN` or `Refs #NN` on the final line, for tooling.

### 6. Wrap and hand back

Hard-wrap the body at 80 columns. If the user asked for a draft, return it for
review. If they authorized the commit or PR, use the draft without asking again.

## Voice

Plain declarative English, one tense throughout the body, backticks for symbols
and commands. The body is prose: paragraphs and an occasional bullet list.
Review triage, test tables, and generated-by footers belong in a PR comment,
where they inform the reviewer without entering the permanent log.

Watch for _leaked frames_: references that parse only from inside the session
that produced them ("as discussed", "the earlier approach", "round 3 of
review"). From inside they read as clear, which is why the writer cannot see
them. The reader has the repo and nothing else.

## Anti-patterns

| Don't                                                   | Why                                                                                                                   |
| ------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| Accept the default squash message or `gh pr create --fill` | Both concatenate the branch's WIP commits. That is noise in trunk forever.                                         |
| Narrate the diff                                        | Listing files or restating hunks doubles the length and buries the why, the one thing the message uniquely adds.      |
| Skip the body on a "small" change                       | The change may be small; the reason rarely is. One sentence still helps.                                              |
| Put issue numbers in the headline                       | They eat the 50 characters, and tooling reads them from the body anyway.                                              |
| Write "see PR"                                          | In two years the PR is archived, link-rotted, or behind an org boundary.                                              |
| Use markdown headers, bold, or tables in the body       | They render as literal `##` and `**` in `git log`, and they signal a change inventory rather than an explanation.     |

## Examples

A routine change, finished at the lede:

```
ci: run the scalafmt version .scalafmt.conf pins in the format check

The version of scalafmt we were running in CI was whatever was on the
AMI, which comes from who-knows-where. Some runner AMIs have newer
versions than others, which was resulting in inconsistent CI runs and
impossible-to-pass CI checks.

The fix is to pin the version of scalafmt the workflow uses to the one
the repo demands.
```

A change that earned a second paragraph and a note for the release:

```
fix(classify): write the resolved doc type back to the document row

Classify recorded its label on classification_run and the cascade
envelope but never on document.doc_type_id, so every classified
document stayed type 0 forever and campaign cohorts, the failure
survey, and the coming per-type coalescing policy never saw it.
write_classification_run now types the row in the same transaction
that completes the run, only when the row still reads 0: a source-
supplied type is authoritative and rides back on doc.extracted, so an
operator re-run that disagrees keeps the row and logs both ids. The
completion log line carries the outcome.

Side effect worth noting in the release: cohort previews and the
failure survey widen to include classified documents.

Closes #448. Refs #391, #392 (per-doc-type coalescing, step 0).
```
