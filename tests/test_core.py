import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout

from unit_style_checker.cli import main
from unit_style_checker.core import check_text


def codes(text):
    return [i.code for i in check_text(text)[0]]


class RuleTests(unittest.TestCase):
    def test_missing_space(self):
        issues, _ = check_text("We added 5mg of salt and 10 mL water.")
        self.assertEqual([(i.code, i.match) for i in issues], [("no-space-unit", "5mg")])
        self.assertEqual(issues[0].suggestion, "insert a (thin) space: '5 mg'")

    def test_compound_words_not_flagged(self):
        self.assertEqual(codes("A 3D model with 2m-long rods and a 5mg/kg dose"), [])

    def test_degrees(self):
        self.assertEqual(codes("at 37 \u00b0C and 4\u00b0C"), ["degree-space", "degree-nospace"])

    def test_micro_times_minus_range(self):
        c = codes("Add 5 ug, use 3 x 10^5 cells, cool to -20 mm, range 10-20 mg, p = .05, 3 hrs")
        for code in ("ug-ascii", "x-for-times", "hyphen-minus", "range-hyphen", "leading-decimal", "sec-hr"):
            self.assertIn(code, c)

    def test_urls_and_citations_ignored(self):
        self.assertEqual(codes("See https://x.org/5mg and \\cite{smith5mg} doi 10.1000/5mg"), [])


class ConsistencyTests(unittest.TestCase):
    def test_mixed_styles(self):
        _, cons = check_text("We used 5 mg, then 7mg, 10% and 20 % and 5 ml plus 3 mL.")
        joined = " ".join(cons)
        self.assertIn("mixed number-unit spacing", joined)
        self.assertIn("mixed percent spacing", joined)
        self.assertIn("'ml' and 'mL'", joined)

    def test_cli_exit_codes(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "a.txt")
            with open(p, "w", encoding="utf-8") as fh:
                fh.write("Clean text with 5 mg and 10%.")
            with redirect_stdout(io.StringIO()):
                self.assertEqual(main([p]), 0)
            with open(p, "w", encoding="utf-8") as fh:
                fh.write("Line one\nDirty 5mg here")
            with redirect_stdout(io.StringIO()) as buf:
                self.assertEqual(main([p]), 1)
            self.assertIn(":2:7: [no-space-unit]", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
