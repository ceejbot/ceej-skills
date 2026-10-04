# Editing an existing memory

Use export → edit the file → import for long or multi-section memories,
including `current-focus`, hubs, and cold logs. A short spoke may use
`memorize` with the same mnemonic and full tag set only when its complete
body is visible and easy to review. `memorize` replaces the whole body;
reconstructing a long body in a tool argument can silently drop text.

## Export, patch, verify

1. **Export fresh** to a scratch directory and keep that export unchanged
   as the before-copy:

   ```
   export(directory = "<scratch>/before", tags = ["project:<slug>"])
   ```

   For a memory outside that project, use its own tag; if the target is
   missing, export without a tag filter. Find the file by its exact
   frontmatter mnemonic, not a guessed filename.
2. **Stage only the memories being changed** in a separate directory,
   copying their exported files intact. Preserve the frontmatter, especially
   UUID, mnemonic, aliases, tags, and links: import uses the UUID to update
   the existing memory. Patch the body in place with a file-editing tool or
   script, keeping untouched text verbatim. Work from the exported file,
   even if a recalled version is already in context.
3. **Review the diff** against the before-copy. Every removal must be
   intentional; every unrelated paragraph and open follow-up must survive.
   When retiring text, verify its destination before removing it here.
   If the memory changed in the store since export, take a fresh export
   and reapply the patch before importing.
4. **Import the staged directory only**:

   ```
   import(directory = "<scratch>/edited")
   ```

   Check the result: edits to existing memories should update them, with
   no newly created memories. Keep the before-copy until verification passes.
5. **Verify persisted content and findability.** Take a fresh export into
   another directory and compare each changed memory's body with the edited
   file; check its UUID, aliases, tags, and links too. A successful import
   response or a matching length alone does not prove the text survived.
   Then recall by exact mnemonic with the project tag and confirm the
   returned mnemonic and tags. Repair missing tags with `edit(add_tags =
   [...])` and repeat the filtered recall. Short-spoke `memorize` writes
   need the same content and tag checks.

CLI equivalents are `trivia export --tag 'project:<slug>' <directory>` and
`trivia import <directory>`. Trivia's `edit` tool changes metadata; editing
the exported Markdown file is what changes the body in this workflow.
