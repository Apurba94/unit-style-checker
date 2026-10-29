# unit-style-checker

**Catch `5mg`, `37 ° C`, `5 ug`, `3 x 10^5`, `.05` and `10-20 mg` before the copy editor
does, and detect mixed number/unit styles across a manuscript.**

Part of the *Research Automation Toolkit*: 100 open tools for daily research work.

## Why

SI conventions and journal style guides require a space between a number and its unit, the
micro sign, a true minus and en-dash ranges. Multi-author manuscripts mix styles (`5 mg` in Methods,
`5mg` in Results; `ml` and `mL`). Each inconsistency is small, but together they look sloppy and
generate rounds of proof corrections.

## Rules

| Code | Example | Suggestion |
|------|---------|------------|
| `no-space-unit` | `5mg` | `5 mg` |
| `degree-space` / `degree-nospace` | `37 ° C`, `4°C` | `37 °C` |
| `percent-space` | `10 %` | `10%` (journal-dependent) |
| `ug-ascii` | `5 ug` | `5 µg` |
| `x-for-times` | `3 x 10^5` | `3 × 10^5` |
| `hyphen-minus` | `-20 mm` | `−20 mm` |
| `range-hyphen` | `10-20 mg` | `10–20 mg` |
| `leading-decimal` | `.05` | `0.05` |
| `plural-unit`, `sec-hr` | `3 hrs`, `5 sec` | `3 h`, `5 s` |

Plus document-level consistency checks (spacing, percent style, `ml`/`mL`, decimal separators).
URLs, DOIs, citation keys and compound modifiers (`5mg/kg`, `2m-long`) are ignored.

## Usage

```bash
pip install .
unit-style-checker manuscript.tex
unit-style-checker methods.md --only no-space-unit,ug-ascii
unit-style-checker paper.txt --json
```

## Testing

```bash
python -m unittest discover -s tests -t .
```

## License

MIT (c) JANIN A APURBA
