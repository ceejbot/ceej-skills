---
name: deep-dive
description: Explore a plan, decision, or idea together until nothing is silently assumed. Use when the user says "deep dive" / "explore this with me" / "stress-test my thinking", or before acting on a plan that still carries unexamined decisions.
---

# Deep Dive

A joint exploration of a plan, decision, or idea. Map the territory as a **design tree**: every decision branches into the decisions that hang off it. The goal is shared understanding, and both parties bring assumptions to surface — yours as much as the user's.

Work the tree in **rounds**. The **frontier** is every decision whose prerequisites are already settled: the questions you can ask _now_ without guessing at answers you haven't heard yet. Ask the whole frontier in one round: number each question and give your recommended answer. Then wait for the user's answers before the next round.

Format a round like so:

```
❓ **Q1** - **<question title>**: <question body, might be multiple paragraphs, including multiple choices>

➡️ <your recommended answer>

---

❓ **Q2** - **<question title>**: <question body, might be multiple paragraphs, including multiple choices>

➡️ <your recommended answer>
```

Your own assumptions are branches of the tree. When you notice yourself filling in an unstated requirement, that's a frontier question: put it to the user with your recommendation attached, the same round it surfaces.

Each round the user answers reshapes the tree: settled decisions push the frontier outward and unblock questions that depended on them. Recompute the frontier and ask the next round. A question whose answer depends on another question still open in this round belongs to a _later_ round, not this one.

Finding _facts_ is your job, never the user's. When a frontier question needs a fact from the environment (filesystem, code, docs, tools), dispatch a sub-agent to find it. Don't block on it: a running exploration is an unsettled prerequisite, so only the questions downstream of it wait for the sub-agent to report; ask the rest of the frontier now. When a frontier question can't be answered by reasoning or lookup — it has to be felt out in running code — invoke the `prototype` skill and let the answer come back as a settled prerequisite. The _decisions_ are made together: put each to the user and wait.

## Capture as you go

When a term crystallises or a hard-to-reverse decision settles mid-dive, invoke the `domain-modeling` skill and capture it on the spot — terms into the `CONTEXT.md` glossary, qualifying decisions into ADRs. Capture happens the moment something settles; a batch at the end loses the reasoning that was fresh when it settled.

When the dive converges on a non-trivial technical direction that deserves a full document, hand off to the `write-design-doc` skill if it's available — the settled tree hands its first four sections a running start.

## Ending the dive

The dive is done when the frontier is empty and **both** parties confirm the understanding is shared: ask the user directly, and state any residual uncertainty of your own rather than carrying it into the work. Act on the plan only after that confirmation.

Before closing, if the trivia MCP is available, offer to memorize the settled decisions and rejected alternatives that didn't earn an ADR, tagged `project:<slug>` per the project's conventions. Without trivia, the glossary and ADRs are the record, and they're enough.

---

Adapted from Matt Pocock's [`grilling`](https://github.com/mattpocock/skills) skill (MIT), reframed from interrogation to mutual exploration.
