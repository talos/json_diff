#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Script for comparing two objects

Copyright (c) 2011, Red Hat Corp.

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
from __future__ import division, absolute_import, print_function
import json
import odict
import logging
from optparse import OptionParser

__author__ = "Matěj Cepl"
__version__ = "0.1.0"

logging.basicConfig(format='%(levelname)s:%(funcName)s:%(message)s', level=logging.DEBUG)

STYLE_MAP = {
    u"_append": "append_class",
    u"_remove": "remove_class",
    u"_update": "update_class"
}
INTERNAL_KEYS = set(STYLE_MAP.keys())

LEVEL_INDENT = "&nbsp;"

out_str_template = u"""
<!DOCTYPE html>
<html lang='en'>
<meta charset="utf-8" />
<title>%s</title>
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
  <h1>%s</h1>
  <table>
  %s
"""

class HTMLFormatter(object):

    def __init__(self, diff_object):
        self.diff = diff_object

    def _generate_page(self, in_dict, title="json_diff result"):
        out_str = out_str_template % (title, title,
            self._format_dict(in_dict))
        out_str += """</table>
  </body>
</html>"""
        return out_str

    @staticmethod
    def _is_scalar(value):
        return not isinstance(value, (list, tuple, dict))

    def _format_item(self, item, index, typch, level=0):
        level_str = ("<td>" + LEVEL_INDENT + "</td>") * level

        if self._is_scalar(item):
            out_str = ("<tr>\n  %s<td class='%s'>%s = %s</td>\n  </tr>\n" %
                (level_str, STYLE_MAP[typch], index, unicode(item)))
        elif isinstance(item, (list, tuple)):
            out_str = self._format_array(item, typch, level+1)
        else:
            out_str = self._format_dict(item, typch, level+1)
        return out_str.strip()

    def _format_array(self, diff_array, typch, level=0):
        out_str = ""
        for index in range(len(diff_array)):
            out_str += self._format_item(diff_array[index], index, typch, level)
        return out_str.strip()

    # doesn't have level and neither concept of it, much
    def _format_dict(self, diff_dict, typch="unknown_change", level=0):
        out_str = ""
        logging.debug("out_str = %s", out_str)

        logging.debug("----------------------------------------------------------------")
        logging.debug("diff_dict = %s", unicode(diff_dict))
        logging.debug("level = %s", unicode(level))
        logging.debug("diff_dict.keys() = %s", unicode(diff_dict.keys()))

        # For all STYLE_MAP keys which are present in diff_dict
        for typechange in set(diff_dict.keys()) & INTERNAL_KEYS:
            out_str += self._format_dict(diff_dict[typechange], typechange, level)

        # For all other non-internal keys
        for variable in set(diff_dict.keys()) - INTERNAL_KEYS:
            out_str += self._format_item(diff_dict[variable], variable, typch, level)

        return out_str.strip()

    def __str__(self):
        return self._generate_page(self.diff).encode("utf-8")

class BadJSONError(ValueError):
    pass

class Comparator(object):
    """
    Main workhorse, the object itself
    """
    def __init__(self, fn1=None, fn2=None, excluded_attrs=(), included_attrs=()):
        if fn1:
            try:
#                self.obj1 = json.load(fn1)
                self.obj1 = odict.odict(json.load(fn1))
            except (TypeError, OverflowError, ValueError) as exc:
                raise BadJSONError("Cannot decode object from JSON.\n%s" % unicode(exc))
        if fn2:
            try:
#                self.obj2 = json.load(fn2)
                self.obj2 = odict.odict(json.load(fn2))
            except (TypeError, OverflowError, ValueError) as exc:
                raise BadJSONError("Cannot decode object from JSON\n%s" % unicode(exc))
        self.excluded_attributes = excluded_attrs
        self.included_attributes = included_attrs

    @staticmethod
    def is_scalar(value):
        """
        Primitive version, relying on the fact that JSON cannot
        contain any more complicated data structures.
        """
        return not isinstance(value, (list, tuple, dict))

    def _compare_arrays(self, old_arr, new_arr):
        """
        simpler version of compare_dicts; just an internal method, becase
        it could never be called from outside.

        We have it guaranteed that both new_arr and old_arr are of type list.
        """
#        for idx in range(len(inters)):
        inters = min(len(old_arr), len(new_arr)) # this is the smaller length
        # max(listA, listB) compares VALUES of items in list, not their length

        result = odict.odict({
            u"_append": {},
            u"_remove": {},
            u"_update": {}
        })
        for idx in range(inters):
            # changed objects, new value is new_arr
            if (type(old_arr[idx]) != type(new_arr[idx])):
                result[u'_update'][idx] = new_arr[idx]
            # another simple variant ... scalars
            elif (self.is_scalar(old_arr)):
                if old_arr[idx] != new_arr[idx]:
                    result[u'_update'][idx] = new_arr[idx]
            # recursive arrays
            elif (isinstance(old_arr[idx], list)):
                res_arr = self._compare_arrays(old_arr[idx],
                    new_arr[idx])
                if (len(res_arr) > 0):
                    result[u'_update'][idx] = res_arr
            # and now nested dicts
            elif isinstance(old_arr[idx], dict):
                res_dict = self.compare_dicts(old_arr[idx], new_arr[idx])
                if (len(res_dict) > 0):
                    result[u'_update'][idx] = res_dict

        # the rest of the larger array
        if (inters == len(old_arr)):
            for idx in range(inters, len(new_arr)):
                result[u'_append'][idx] = new_arr[idx]
        else:
            for idx in range(inters, len(old_arr)):
                result[u'_remove'][idx] = old_arr[idx]

        # Clear out unused keys in result
        out_result = odict.odict({})
        for key in result:
            if len(result[key]) > 0:
                out_result[key] = result[key]

        return out_result

    def compare_dicts(self, old_obj=None, new_obj=None):
        """
        The real workhorse
        """
        if not old_obj and hasattr(self, "obj1"):
            old_obj = self.obj1
        if not new_obj and hasattr(self, "obj2"):
            new_obj = self.obj2

        old_keys = set()
        new_keys = set()
        if old_obj and len(old_obj) > 0:
            old_keys = set(old_obj.keys())
        if new_obj and len(new_obj) > 0:
            new_keys = set(new_obj.keys())

        keys = old_keys | new_keys

        result = odict.odict({
            u"_append": {},
            u"_remove": {},
            u"_update": {}
        })
        for name in keys:
            # Explicitly excluded arguments
            logging.debug("name = %s (inc = %s, excl = %s)", name,
                            unicode(self.included_attributes), unicode(self.excluded_attributes))
            if ((self.included_attributes and (name not in self.included_attributes)) or
                    (name in self.excluded_attributes)):
                continue
            # old_obj is missing
            if name not in old_obj:
                result[u'_append'][name] = new_obj[name]
            # new_obj is missing
            elif name not in new_obj:
                result[u'_remove'][name] = old_obj[name]
            # changed objects, new value is new_obj
            elif (type(old_obj[name]) != type(new_obj[name])):
                result[u'_update'][name] = new_obj[name]
            # last simple variant ... scalars
            elif (self.is_scalar(old_obj[name])):
                if old_obj[name] != new_obj[name]:
                    result[u'_update'][name] = new_obj[name]
            # now arrays (we can be sure, that both old_obj and
            # new_obj are of the same type)
            elif (isinstance(old_obj[name], list)):
                res_arr = self._compare_arrays(old_obj[name],
                    new_obj[name])
                if (len(res_arr) > 0):
                    result[u'_update'][name] = res_arr
            # and now nested dicts
            elif isinstance(old_obj[name], dict):
                res_dict = self.compare_dicts(old_obj[name], new_obj[name])
                if (len(res_dict) > 0):
                    result[u'_update'][name] = res_dict

        # Clear out unused keys in result
        out_result = odict.odict({})
        for key in result:
            if len(result[key]) > 0:
                out_result[key] = result[key]

        return out_result


if __name__ == "__main__":
    usage = "usage: %prog [options] old.json new.json"
    description = "Generates diff between two JSON files."
    parser = OptionParser(usage=usage)
    parser.add_option("-x", "--exclude",
                  action="append", dest="exclude", metavar="ATTR", default=[],
                  help="attributes which should be ignored when comparing")
    parser.add_option("-i", "--include",
                  action="append", dest="include", metavar="ATTR", default=[],
                  help="attributes which should be exclusively used when comparing")
    parser.add_option("-H", "--HTML",
                  action="store_true", dest="HTMLoutput", metavar="BOOL", default=False,
                  help="program should output to HTML report")
    (options, args) = parser.parse_args()

    if len(args) != 2:
        parser.error("Script requires two positional arguments, names for old and new JSON file.")

    diff = Comparator(file(args[0]), file(args[1]), options.exclude, options.include)
    if options.HTMLoutput:
        diff_res = diff.compare_dicts()
        logging.debug("diff_res:\n%s", json.dumps(diff_res, indent=True))
        print(HTMLFormatter(diff_res))
    else:
        outs = json.dumps(diff.compare_dicts(), indent=4, ensure_ascii=False).encode("utf-8")
        outs = "\n".join([line for line in outs.split("\n")])
        print(outs)
