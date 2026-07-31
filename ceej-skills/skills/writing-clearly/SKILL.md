---
name: writing-clearly
description: Use whenever writing or revising prose on the user's behalf — documentation, READMEs, comments, error messages, announcements, blog drafts. A style guide for the user's preferred English: warm, direct, laconic, occasionally devastating.
---

# Writing clearly

Write in a warm but not overly familiar tone. Address the reader as "you". Treat them as a respected colleague who is smart and capable of understanding complex topics. 

Use clear, concise English prose. Don't repeat facts. State things directly. Be laconic, but not so terse as to be impenetrable. It's okay to use the breadth of our very large English vocabulary: programmers are usually verbal people who appreciate wordplay and words in general.

We're not being paid by the word or forced to hit a word count: respect our reader's time and get the information across efficiently and effectively.

It's okay to make jokes. A devastatingly clever pun when the reader least expects it is exactly what I would do. (So long as it doesn't distract from something important.) Subtle wordplay and literary reference are also welcome: I like rewarding readers who are paying attention.

## Words to watch out for

Avoid these words:

- honest
- spine
- seam

Ceej rarely uses them in her writing, and so should you. They are among the tells of AI writing. For most human writers, "honest" carries an echo of its opposite, as Marc Antony's speech makes "honorable" mean its opposite. Find other metaphors! 

## Some usage comments

When documenting software behavior, do not use "will do". Instead say that software "does" something. Example:

- BAD: The process will crash on exception.
- GOOD: The process crashes on exception.

Use the serial comma. It adds clarity every time.

## Composition

Follow the Strunk & White principles of composition as much as possible:

1. Make the paragraph the unit of composition.
2. As a rule, begin each paragraph with a topic sentence.
3. Use the active voice. The active voice is usually more direct and vigorous
than the passive. Especially do not use the passive voice to hide an actor.
4. Put statements in positive form.
5. Use definite, specific, concrete language.
6. Omit needless words.
7. Avoid a succession of loose sentences.
8. Express coordinate ideas in similar form.
9. Keep related words together.
10. In summaries, keep to one tense.
11. Place the emphatic words of a sentence at the end.

The theme of these rules is disciplined economy.

## Demonstrations

Rules are cheap; here's what following them looks like.

- BEFORE: It's important to note that the configuration file will need to be
  updated in order to ensure that the service is able to connect successfully.
- AFTER: Update the configuration file so the service can connect.

- BEFORE: This function is responsible for handling the parsing of user input.
- AFTER: This function parses user input.

- BEFORE: Users should be aware that deleting a workspace is a permanent
  action that cannot be undone.
- AFTER: Deleting a workspace is forever. There is no undo.

The AFTER versions are shorter, but that's a side effect. They put the actor
first, cut the throat-clearing ("it's important to note", "users should be
aware"), and let the emphatic word land at the end.
