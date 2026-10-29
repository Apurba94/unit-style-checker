"""SI / journal style rules for numbers and units."""
import re
from collections import Counter, namedtuple

Issue = namedtuple("Issue", "line col code match suggestion")

UNITS = ["mg", "g", "kg", "ug", "\u00b5g", "ng", "mL", "ml", "L", "\u00b5L", "uL", "nm", "\u00b5m", "um", "mm", "cm",
         "m", "km", "s", "ms", "min", "h", "Hz", "kHz", "MHz", "GHz", "mol", "mmol", "\u00b5mol", "M", "mM", "\u00b5M",
         "nM", "K", "Pa", "kPa", "MPa", "J", "kJ", "W", "kW", "mW", "V", "mV", "A", "mA", "dB", "rpm", "kDa", "Da",
         "bp", "kb", "Mb", "GB", "MB", "TB", "ppm", "\u00b0C"]
_UNIT_ALT = "|".join(sorted((re.escape(u) for u in UNITS if u != "\u00b0C"), key=len, reverse=True))
_NUMBER = r"(?<![\w.])\d+(?:[.,]\d+)?"


def _masked(text):
    def blank(m):
        return re.sub(r"[^\n]", " ", m.group(0))
    text = re.sub(r"(?<!\\)%.*", blank, text) if "\\begin" in text or "\\section" in text else text
    text = re.sub(r"\\(?:cite\w*|ref|label|url|includegraphics)\s*(?:\[[^\]]*\])?\{[^}]*\}", blank, text)
    return re.sub(r"https?://\S+|\b10\.\d{4,9}/\S+", blank, text)


RULES = [
    ("no-space-unit", re.compile(r"(%s)(%s)\b(?![-\u2013/]?\w)" % (_NUMBER, _UNIT_ALT)), "insert a (thin) space: '{0} {1}'"),
    ("degree-space", re.compile(r"(%s)\s+\u00b0\s?C\b" % _NUMBER), "write '{0} \u00b0C' (no space between \u00b0 and C)"),
    ("degree-nospace", re.compile(r"(%s)\u00b0C\b" % _NUMBER), "write '{0} \u00b0C' with a space before \u00b0C"),
    ("percent-space", re.compile(r"(%s)\s+%%(?!\w)" % _NUMBER), "most journals write '{0}%' without a space"),
    ("ug-ascii", re.compile(r"(?<![\w])(\d[\d.]*\s?)(u)(g|L|l|m|M|mol)\b"), "use the micro sign: '\u00b5{2}'"),
    ("x-for-times", re.compile(r"(\d)\s?[xX]\s?(10)(\^?[-\u2212]?\d+)"), "use '\u00d7' (times) for powers of ten"),
    ("hyphen-minus", re.compile(r"(?<![\w-])-(\d+(?:\.\d+)?)\s?(%s)\b" % _UNIT_ALT), "use a true minus sign (\u2212) for negative values"),
    ("range-hyphen", re.compile(r"(%s)-(%s)\s?(%s)\b" % (_NUMBER, r"\d+(?:\.\d+)?", _UNIT_ALT)), "use an en dash for ranges: '{0}\u2013{1} {2}'"),
    ("leading-decimal", re.compile(r"(?<![\w.])(\.\d+)"), "add a leading zero: '0{0}'"),
    ("plural-unit", re.compile(r"(%s)\s?(mgs|kgs|mins|hrs|secs|mls)\b" % _NUMBER), "units have no plural form"),
    ("sec-hr", re.compile(r"(%s)\s?(sec|hr|hrs)\b" % _NUMBER), "use SI symbols: s, h"),
]


def check_text(text, enabled=None):
    """Return (issues, consistency) where consistency reports mixed styles across the document."""
    masked = _masked(text)
    line_starts = [0] + [m.end() for m in re.finditer("\n", masked)]

    def loc(pos):
        import bisect
        i = bisect.bisect_right(line_starts, pos) - 1
        return i + 1, pos - line_starts[i] + 1

    issues = []
    for code, rx, tip in RULES:
        if enabled and code not in enabled:
            continue
        for m in rx.finditer(masked):
            line, col = loc(m.start())
            issues.append(Issue(line, col, code, m.group(0), tip.format(*m.groups())))
    issues.sort(key=lambda i: (i.line, i.col))
    style = Counter()
    for m in re.finditer(r"(%s)(\s?)(%s)\b" % (_NUMBER, _UNIT_ALT), masked):
        style["spaced" if m.group(2) else "unspaced"] += 1
    for m in re.finditer(r"(%s)(\s?)%%" % _NUMBER, masked):
        style["percent_spaced" if m.group(2) else "percent_unspaced"] += 1
    dec = Counter("comma" if "," in m.group(0) else "point" for m in re.finditer(r"\b\d+[.,]\d{1,2}\b(?![.,]\d)", masked))
    consistency = []
    if style["spaced"] and style["unspaced"]:
        consistency.append("mixed number-unit spacing: %d spaced vs %d unspaced" % (style["spaced"], style["unspaced"]))
    if style["percent_spaced"] and style["percent_unspaced"]:
        consistency.append("mixed percent spacing: %d '5 %%' vs %d '5%%'" % (style["percent_spaced"], style["percent_unspaced"]))
    if "ml" in re.findall(r"\d\s?(ml|mL)\b", masked) and "mL" in re.findall(r"\d\s?(ml|mL)\b", masked):
        consistency.append("both 'ml' and 'mL' are used")
    if dec["comma"] and dec["point"]:
        consistency.append("possible mixed decimal separators (comma and point)")
    return issues, consistency
