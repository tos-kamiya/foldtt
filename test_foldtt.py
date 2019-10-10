import unittest
import io

from foldtt import expand_column_at_index, expand_column_at_label, InvalidTargetLabel


class TestFoldTT(unittest.TestCase):
    def test_expand_by_index(self):
        inp = io.StringIO('\n'.join([
            "a\tb1,b2\tc",
            "d\te1, e2\tf",
            "g\th1 ,h2\ti"]) + '\n')
        outp = io.StringIO()
        expand_column_at_index(outp, inp, 1)
        out_str = outp.getvalue()
        self.assertEqual(out_str, '\n'.join([
            "a\tb1\tc",
            "a\tb2\tc",
            "d\te1\tf",
            "d\te2\tf",
            "g\th1 \ti",
            "g\th2\ti"]) + '\n')

    def test_expand_by_label(self):
        inp = io.StringIO('\n'.join([
            "A\tB\tC",
            "a\tb1,b2\tc",
            "d\te1, e2\tf",
            "g\th1 ,h2\ti"]) + '\n')
        outp = io.StringIO()
        expand_column_at_label(outp, inp, "B")
        out_str = outp.getvalue()
        self.assertEqual(out_str, '\n'.join([
            "A\tB\tC",
            "a\tb1\tc",
            "a\tb2\tc",
            "d\te1\tf",
            "d\te2\tf",
            "g\th1 \ti",
            "g\th2\ti"]) + '\n')

    def test_expand_by_label_with_invalid_label(self):
        inp = io.StringIO('\n'.join([
            "A\tB\tC",
            "a\tb1,b2\tc",
            "d\te1, e2\tf",
            "g\th1 ,h2\ti"]) + '\n')
        outp = io.StringIO()
        with self.assertRaises(InvalidTargetLabel):
            expand_column_at_label(outp, inp, "D")


if __name__ == '__main__':
    unittest.main(verbosity=2)
