# -*- coding: utf-8 -*-
"""
PyUnit unit tests
"""
from __future__ import division, absolute_import, unicode_literals
import unittest
import json
import json_diff
from io import StringIO
import codecs

SIMPLE_OLD = """
{
    "a": 1,
    "b": true,
    "c": "Janošek"
}
"""

SIMPLE_NEW = """
{
    "b": false,
    "c": "Maruška",
    "d": "přidáno"
}
"""

SIMPLE_DIFF =  """
{
    "_append": {
        "d": "přidáno"
    },
    "_remove": {
        "a": 1
    },
    "_update": {
        "c": "Maruška",
        "b": false
    }
}
"""

SIMPLE_DIFF_HTML="""
<!DOCTYPE html>
<html lang='en'>
<meta charset="utf-8" />
<title>json_diff result</title>
<style>
td {
text-align: center;
}
.append_class {
color: green;
}
.remove_class {
color: red;
}
.update_class {
color: navy;
}
</style>
<body>
<h1>json_diff result</h1>
<table>
<tr>
<td class='remove_class'>a = 1</td>
</tr><tr>
<td class='update_class'>c = Maruška</td>
</tr><tr>
<td class='update_class'>b = False</td>
</tr><tr>
<td class='append_class'>d = přidáno</td>
</tr>
</table>
</body>
</html>
"""

SIMPLE_ARRAY_OLD = """
{
   "a": [ 1 ]
}
"""

SIMPLE_ARRAY_NEW = """
{
   "a": [ 1, 2 ]
}
"""

SIMPLE_ARRAY_DIFF = """
{
    "_update": {
        "a": {
            "_append": {
                "1": 2
            }
        }
    }
}
"""

NESTED_OLD = """
{
    "a": 1,
    "b": 2,
    "son": {
        "name": "Janošek"
    }
}
"""

NESTED_NEW = """
{
    "a": 2,
    "c": 3,
    "daughter": {
        "name": "Maruška"
    }
}
"""

NESTED_DIFF = """
{
    "_append": {
        "c": 3,
        "daughter": {
            "name": "Maruška"
        }
    },
    "_remove": {
        "b": 2,
        "son": {
            "name": "Janošek"
        }
    },
    "_update": {
        "a": 2
    }
}
"""
NESTED_DIFF_EXCL = """
{
    "_append": {
        "c": 3
    },
    "_remove": {
        "b": 2
    },
    "_update": {
        "a": 2
    }
}
"""

ARRAY_OLD = """
{
    "a": 1,
    "b": 2,
    "children": [
        "Pepíček", "Anička", "Maruška"
    ]
}
"""

ARRAY_NEW = """
{
    "a": 1,
    "children": [
        "Pepíček", "Tonička", "Maruška"
    ],
    "c": 3
}
"""

ARRAY_DIFF = """
{
    "_remove": {
        "b": 2
    },
    "_append": {
        "c": 3
    },
    "_update": {
        "children": [
            "Pepíček",
            "Tonička",
            "Maruška"
        ]
    }
}
"""

class TestHappyPath(unittest.TestCase):
    def _run_test(self, oldf, newf, difff, msg="", inc=(), exc=()):
        diffator = json_diff.Comparator(oldf, newf, inc, exc)
        diff = diffator.compare_dicts()
        expected = json.load(difff)
        self.assertEqual(json.dumps(diff, sort_keys=True), json.dumps(expected, sort_keys=True),
                         msg + "\n\nexpected = %s\n\nobserved = %s" %
                         (json.dumps(expected, sort_keys=True, indent=4, ensure_ascii=False),
                          json.dumps(diff, sort_keys=True, indent=4, ensure_ascii=False)))

    def _run_test_formatted(self, oldf, newf, difff, msg=""):
        diffator = json_diff.Comparator(oldf, newf)
        diff = ("\n".join([line.strip() \
                for line in unicode(json_diff.HTMLFormatter(diffator.compare_dicts())).split("\n")])).strip()
        expected = ("\n".join([line.strip() for line in difff if line])).strip()
        self.assertEqual(diff, expected, msg +
                         "\n\nexpected = %s\n\nobserved = %s" %
                         (expected, diff))

    def test_empty(self):
        diffator = json_diff.Comparator({}, {})
        diff = diffator.compare_dicts()
        self.assertEqual(json.dumps(diff).strip(), "{}",
             "Empty objects diff.\n\nexpected = %s\n\nobserved = %s" %
             ({}, diff))

    def test_simple(self):
        self._run_test(StringIO(SIMPLE_OLD), StringIO(SIMPLE_NEW), StringIO(SIMPLE_DIFF),
                "All-scalar objects diff.")

    def test_simple_formatted(self):
        self._run_test_formatted(StringIO(SIMPLE_OLD), StringIO(SIMPLE_NEW),
            StringIO(SIMPLE_DIFF_HTML),
            "All-scalar objects diff (formatted).")

    def test_simple_array(self):
        self._run_test(StringIO(SIMPLE_ARRAY_OLD), StringIO(SIMPLE_ARRAY_NEW),
            StringIO(SIMPLE_ARRAY_DIFF), "Simple array objects diff.")

    def test_realFile(self):
        self._run_test(open("test/old.json"), open("test/new.json"),
            open("test/diff.json"), "Simply nested objects (from file) diff.")

    def test_nested(self):
        self._run_test(StringIO(NESTED_OLD), StringIO(NESTED_NEW),
            StringIO(NESTED_DIFF), "Nested objects diff.")

    # def test_nested_excluded(self):
        # self._run_test(StringIO(NESTED_OLD), StringIO(NESTED_NEW),
            # StringIO(NESTED_DIFF_EXCL), "Nested objects diff.", exc=("name"))

#    def test_piglit_results(self):
#        self._run_test(open("test/old-testing-data.json"), open("test/new-testing-data.json"),
#            open("test/diff-testing-data.json"), "Large piglit results diff.")

    def test_nested_formatted(self):
        self._run_test_formatted(open("test/old.json"), open("test/new.json"),
            codecs.open("test/nested_html_output.html", "r", "utf-8"),
            "Simply nested objects (from file) diff formatted as HTML.")

NO_JSON_OLD = """
THIS IS NOT A JSON STRING
"""

NO_JSON_NEW = """
AND THIS NEITHER
"""


class TestSadPath(unittest.TestCase):
    def test_no_JSON(self):
        self.assertRaises(json_diff.BadJSONError,
                json_diff.Comparator, StringIO(NO_JSON_OLD), StringIO(NO_JSON_NEW))


if __name__ == "__main__":
    unittest.main()
