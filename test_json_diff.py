# -*- coding: utf-8 -*-
"""
PyUnit unit tests
"""
from __future__ import division, absolute_import
import unittest
import json
import json_diff
from StringIO import StringIO

SIMPLE_OLD = u"""
{
    "a": 1,
    "b": true,
    "c": "Janošek"
}
"""

SIMPLE_NEW = u"""
{
    "b": false,
    "c": "Maruška",
    "d": "přidáno"
}
"""

SIMPLE_DIFF =  u"""
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

NESTED_OLD = u"""
{
    "a": 1,
    "b": 2,
    "son": {
        "name": "Janošek"
    }
}
"""

NESTED_NEW = u"""
{
    "a": 2,
    "c": 3,
    "daughter": {
        "name": "Maruška"
    }
}
"""

NESTED_DIFF = u"""
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

class TestHappyPath(unittest.TestCase):
    def test_empty(self):
        diffator = json_diff.Comparator({}, {})
        diff = diffator.compare_dicts()
        self.assertEqual(json.dumps(diff).strip(), "{}",
             "Empty objects diff.\n\nexpected = %s\n\nobserved = %s" %
             (str({}), str(diff)))

    def test_simple(self):
        diffator = json_diff.Comparator(StringIO(SIMPLE_OLD), StringIO(SIMPLE_NEW))
        diff = diffator.compare_dicts()
        expected = json.loads(SIMPLE_DIFF)
        self.assertEqual(diff, expected, "All-scalar objects diff." +
                         "\n\nexpected = %s\n\nobserved = %s" %
                         (str(expected), str(diff)))

    def test_realFile(self):
        diffator = json_diff.Comparator(open("test/old.json"), open("test/new.json"))
        diff = diffator.compare_dicts()
        expected = json.load(open("test/diff.json"))
        self.assertEqual(diff, expected, "Simply nested objects (from file) diff." +
                         "\n\nexpected = %s\n\nobserved = %s" %
                         (str(expected), str(diff)))

    def test_nested(self):
        diffator = json_diff.Comparator(StringIO(NESTED_OLD), StringIO(NESTED_NEW))
        diff = diffator.compare_dicts()
        expected = json.loads(NESTED_DIFF)
        self.assertEqual(diff, expected, "Nested objects diff. " +
                         "\n\nexpected = %s\n\nobserved = %s" %
                         (str(expected), str(diff)))
    
    def test_nested_formatted(self):
        diffator = json_diff.Comparator(open("test/old.json"), open("test/new.json"))
        diff = "\n".join([line.strip() \
                for line in str(json_diff.HTMLFormatter(diffator.compare_dicts())).split("\n")])
        expected = "\n".join([line.strip() for line in open("test/nested_html_output.html").readlines()])
        self.assertEqual(diff, expected, "Simply nested objects (from file) diff formatted as HTML." +
                         "\n\nexpected = %s\n\nobserved = %s" %
                         (expected, diff))
    
    def test_large_with_exclusions(self):
        diffator = json_diff.Comparator(open("test/old-testing-data.json"),
                    open("test/new-testing-data.json"), ('command', 'time'))
        diff = diffator.compare_dicts()
        expected = json.load(open("test/diff-testing-data.json"))
        self.assertEqual(diff, expected, "Large objects with exclusions diff." +
                         "\n\nexpected = %s\n\nobserved = %s" %
                         (str(expected), str(diff)))


NO_JSON_OLD = u"""
THIS IS NOT A JSON STRING
"""

NO_JSON_NEW = u"""
AND THIS NEITHER
"""


class TestSadPath(unittest.TestCase):
    def test_no_JSON(self):
        self.assertRaises(json_diff.BadJSONError,
                json_diff.Comparator, StringIO(NO_JSON_OLD), StringIO(NO_JSON_NEW))


if __name__ == "__main__":
    unittest.main()
