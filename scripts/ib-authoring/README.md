# IB content authoring

These offline Python builders preserve the separately authored numerical variants
and the symbolic/numerical assertions used during review. They are not part of
the website runtime or its npm build. Runtime content is the committed JSON in
`content/ib/math-aa-hl/`.

Install `requirements.txt` in an isolated Python environment, then run a selected
builder from any working directory, for example:

```sh
python scripts/ib-authoring/functions.py
npm run verify:ib-question-bank
```

Builders rewrite their collection atomically. Review the resulting diff before
publication; a successful calculation or schema check does not replace reviewing
the question's wording, domains, difficulty or allocation of marks. Preserve any
later editorial corrections in the builder as well as its generated JSON.

`reference-metadata/` contains only question numbers, maximum marks, difficulty
and any printed calculator labels. The user-supplied reference PDFs and original
question text are excluded. Significant reconstruction choices and review
coverage are documented in `docs/ib-content-reviews/`.
