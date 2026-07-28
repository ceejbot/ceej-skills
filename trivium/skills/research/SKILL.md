---
name: research
description: Use when the user asks to investigate or research a topic across sources — JIRA, GitHub, Notion, Slack, the web — or to continue a prior investigation. Triggers on "research X", "investigate X", "dig into", "continue the research on X". Stores findings as cited trivia memories so a later session can pick up where this one stopped.
---

# Research

**Core principle**: act as a librarian and research assistant. Investigate
sources, surface facts that *seem relevant* to the research, store them in
a structured fashion along with citation information so they can be referenced
later. If there are no citations, you do not have a memory. Findings live in
the trivia MCP ([chrisdickinson/trivia](https://github.com/chrisdickinson/trivia)
— setup instructions are Rust-oriented, but it's quite good).

## When to use

- The user asks you to investigate a topic, or to continue an investigation
  already in progress.
- The investigation may span different sources: JIRA, GitHub, Notion, Slack,
  the internet — essentially all available tools. The user will likely scope
  the research to one or more avenues.

**Skip if:** the question is answerable with a single lookup from one obvious
source. Just answer it. An investigation that leaves no memories behind isn't
research.

## Steps

### 1. Find or create the root memory

Every investigation hangs off one root memory:

- Tag: `research/<project>`
- Mnemonic: `Core memory for <project> research`. Embellish if this lands too
  close to other memories.

If the user gave you a tag, use it. Otherwise recall for relevant
investigations by mnemonic. Then:

- No root memory exists → create one and generate a tag.
- Exactly one matches → use it.
- Multiple match with no clear winner → ask the user to pick.

### 2. Consult memory before researching

If you can recall a memory that sufficiently covers the user's question, show
it to them. If the memory is older than a few days, confirm it against its
cited source: outdated → rate it not useful and continue investigating; still
good → rate it useful and **stop here**. This step exists so you don't re-buy
facts the library already holds.

### 3. Fan out agents

Launch one agent per source the user scoped (Notion, JIRA, Slack, GitHub, web),
concurrently. Agents never see this skill — the prompt is the contract, so it
must carry the tag and the memory format verbatim. Template:

> Research this question: <question>. Search <source> only.
>
> For each finding relevant to the question, store one memory using the trivia
> `memorize` tool:
> - tags: `["research/<project>", "research/<project>/<source>"]`
> - mnemonic: a short specific handle for the finding
> - body: a 1-sentence finding as the lede, then 1–3 sentences of detail. No
>   adverbs. Drop value judgements. Be laconic. State just the facts as they
>   relate to the question.
> - citations as the trailing content, one line per source, in exactly this
>   form. The URL must be something usable to refetch the information:
>   `- [Title](URL, URN, or identifier) (<channel>; originated YYYY-MM-DDTHH:MM:SS; fetched YYYY-MM-DDTHH:MM:SS)`
> - If there are no citations, you do not have a memory. Skip it.
>
> Return the list of mnemonics you stored, one per line, each with a
> half-sentence gloss.

### 4. Review, link, rate

Once the agents report back, do a fast review pass: recall all memories tagged
`research/<project>`, link each agent memory to the root memory, and rate —
up for solid cited findings, down for weak or duplicate ones. This is the
quality gate; agents record generously and the review prunes.

### 5. Present results

Show the user the most relevant findings, with citations, and name the
investigation tag so a future session can continue with it.

## Memory format

Example memory, given a prompt:

```markdown
Found evidence that `Pending` enum variant was not used by UI.

`Pending` was introduced early in project to align with a prototype
implementation, but it is not in use by the production UI.

- [Commit <sha>: introduction of Pending](https://github.com/chrisdickinson/clams/...) (Github; originated 2020-01-04T13:33:00; fetched 2025-01-03T03:30:00)
- [Slack thread: "What does pending do exactly?"](https://slack.com/<CID>/<MSGID>) (Slack; originated 2023-12-31T03:30:30; fetched 2025-01-03T03:30:00)
```

## Anti-patterns

| Don't | Why |
|---|---|
| Store a memory without citations | It can't be verified or refetched. No citations, no memory. |
| Editorialize in memory bodies | Adverbs and value judgements rot. Facts with citations survive. |
| Re-research a question memory already answers | Step 2 exists to stop this. Confirm staleness against the cited source instead. |
| Let agents freelance the memory format | They never saw this skill. The step-3 template is the contract — send it verbatim. |
| Tag agent memories with anything other than the exact root tag | The step-4 review recalls by `research/<project>`; a drifted tag orphans the finding. |
| Skip the review pass | Unrated, unlinked agent memories pollute future recall. The prune is part of the job. |
