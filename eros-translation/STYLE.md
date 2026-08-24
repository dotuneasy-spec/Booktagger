# Translation style guide — Verga, *Eros* (1884)

Literary English translation of a 19th-century Italian society novel. Aim for the tone of a good Victorian/Edwardian novel: elegant, slightly formal, never slangy, never academic-footnote-ish.

## Source

- Italian files: `/workspace/eros-translation/italian/chapter_NN.txt`
- Edition: public-domain 1884 Treves (5th ed.) via Wikisource
- Output: `/workspace/eros-translation/english/chapter_NN.md`

## Output format

Each file must be exactly:

```
# Chapter XII

First paragraph...

Second paragraph...
```

- Use Arabic chapter numbers in the heading matching the Roman numeral of the source (`I` → `Chapter I` is also fine; prefer `# Chapter I` with Roman numerals as in the original).
- Separate paragraphs with a blank line.
- Do **not** include the Italian heading `EROS` / `XII.` — only the English chapter heading.
- Do **not** add translator notes, footnotes, commentary, or summaries.
- Translate **every** sentence. Do not omit, condense, or skip dialogue.

## Dialogue

Convert Italian dashes to English quotation marks.

Italian:
```
— Che rumore è cotesto? domandò dopo un lungo silenzio.
```

English:
```
“What noise is that?” she asked after a long silence.
```

- Use curly quotes if convenient; straight `"` is acceptable.
- Keep dialogue tags (`he said`, `she asked`) in the same sentence when the Italian does.
- When a speech and its narrative continuation share a paragraph in Italian, keep them together.

## Names, titles, places

Keep Italian titles and surnames:

- Marchese / Marchesa Alberti (not Marquis/Marchioness, except in the rare case of a generic English equivalent already in the source)
- Contessa / Contessina
- Signor, Signora, Signorina (or “the young lady” when `signorina` is used descriptively)
- Alberto Alberti, Adele Forlani, Velleda Manfredini, Emilia / the Contessa Armandi, Gemmati, Bartolomeo Forlani, Cecilia Alberti
- Belmonte, Florence (for Firenze), Milan (Milano), Prato, Bellagio, Leghorn (Livorno) or Livorno — use **Florence, Milan, Turin, Leghorn, the Cascine, La Scala**
- Collegio Cicognini → the Cicognini College (or “Cicognini boarding-school”)
- *dominò* (masquerade cloak) → “domino”
- *voi* among adults of this class → ordinary English “you” (formal register, never *thou*)

## Register and diction

- Prefer “had” over “had got”; “upon” is fine when it sounds period-appropriate.
- Keep Verga’s long periodic sentences; do not chop them into modern short prose unless English grammar forces a split.
- Em-dashes for Italian `—` used as parenthetical asides.
- Ellipses for trailing speech: `...`
- Preserve irony, coldness, and melodramatic heat. Do not moralize or modernize attitudes.
- Archaic Italian (`cotesto`, `poscia`, `allorchè`, `sè`, `colezione`) → natural literary English, not mock-antique.

## Sample (opening of Chapter I)

Italian:
> Verso le quattro di una fra le ultime notti del carnevale, la marchesa Alberti, seduta dinanzi allo specchio, e alquanto pallida, stava guardandosi con occhi stanchi e distratti, mentre la cameriera le acconciava i capelli per la notte.

English:
> Toward four o’clock on one of the last nights of Carnival, the Marchesa Alberti, seated before the mirror and somewhat pale, was looking at herself with tired, absent eyes while her maid dressed her hair for the night.

Italian:
> — Che rumore è cotesto? domandò dopo un lungo silenzio.
> — La carrozza del signor marchese.
> — Così presto! mormorò essa soffocando uno sbadiglio.

English:
> “What noise is that?” she asked after a long silence.
> “The Marchese’s carriage.”
> “So soon!” she murmured, stifling a yawn.

## Completeness check

When finished, each English chapter should be roughly similar in length to the Italian (typically 90–120% of the Italian word count). If it is much shorter, something was omitted.

Write only the markdown chapter file(s) assigned to you. No README, no extra commentary files.
