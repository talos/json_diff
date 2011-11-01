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
from __future__ import division, absolute_import
import json
import logging
import argparse

__author__ = "Matěj Cepl"
__version__ = "0.1.0"

logging.basicConfig(format='%(levelname)s:%(funcName)s:%(message)s', level=logging.INFO)

STYLE_MAP = {
    u"_append": "append_class",
    u"_remove": "remove_class",
    u"_update": "update_class"
}


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
</html>
        """
        return out_str

    @staticmethod
    def _is_scalar(value):
        return not isinstance(value, (list, tuple, dict))

    def _is_leafnode(self, node):
        # anything else than dict shouldn't happen here, so that would be
        # pure error
        assert(isinstance(node, dict))
        # the following lines mean that it is an expression
        out = True
        for key in node:
            if not self._is_scalar(node[key]):
                out = False
        return out

    # doesn't have level and neither concept of it, much
    def _format_dict(self, diff_dict, typch="unknown_change", level=0):
        internal_keys = set(STYLE_MAP.keys())
        level_str = ("<td>" + LEVEL_INDENT + "</td>") * level
        out_str = ""
        logging.debug("out_str = %s", out_str)

        logging.debug("----------------------------------------------------------------")
        logging.debug("diff_dict = %s", unicode(diff_dict))
        logging.debug("level = %s", unicode(level))
        logging.debug("diff_dict.keys() = %s", unicode(diff_dict.keys()))

        for typechange in set(diff_dict.keys()) & internal_keys:
            logging.debug("---- internal typechange in diff_dict.keys() = %s", typechange)
            logging.debug("---- diff_dict[typechange] = %s", unicode(diff_dict[typechange]))
            logging.debug("---- self._is_leafnode(diff_dict[typechange]) = %s",
                self._is_leafnode(diff_dict[typechange]))
            out_str += self._format_dict(diff_dict[typechange], typechange, level)

        for variable in set(diff_dict.keys()) - internal_keys:
            logging.debug("**** external variable in diff_dict.keys() = %s", variable)
            logging.debug("**** diff_dict[variable] = %s", unicode(diff_dict[variable]))
            logging.debug("**** self._is_scalar(diff_dict[variable]) = %s",
                self._is_scalar(diff_dict[variable]))
            if self._is_scalar(diff_dict[variable]):
                out_str += ("<tr>\n  %s<td class='%s'>%s = %s</td>\n  </tr>\n" %
                    (level_str, STYLE_MAP[typch], variable, unicode(diff_dict[variable])))
                logging.debug("out_str = %s", out_str)
            else:
                out_str += self._format_dict(diff_dict[variable], None, level+1)

        return out_str.strip()

    
    def __str__(self):
        return self._generate_page(self.diff).encode("utf-8")

class BadJSONError(ValueError):
    pass

class Comparator(object):
    """
    Main workhorse, the object itself 
    """
    def __init__(self, fn1=None, fn2=None, excluded_attrs=()):
        if fn1:
            try:
                self.obj1 = json.load(fn1)
            except (TypeError, OverflowError, ValueError) as exc:
                raise BadJSONError("Cannot decode object from JSON.\n%s" % unicode(exc))
        if fn2:
            try:
                self.obj2 = json.load(fn2)
            except (TypeError, OverflowError, ValueError) as exc:
                raise BadJSONError("Cannot decode object from JSON\n%s" % unicode(exc))
        self.excluded_attributes = excluded_attrs

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
        """
        inters = min(old_arr, new_arr)

        result = {
            "_append": {},
            "_remove": {},
            "_update": {}
        }        
        for idx in range(len(inters)):
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
    
        # Clear out unused inters in result
        out_result = {}
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

        result = {
            "_append": {},
            "_remove": {},
            "_update": {}
        }        
        for name in keys:
            # Explicitly excluded arguments
            if (name in self.excluded_attributes):
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
            # now arrays
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
        out_result = {}
        for key in result:
            if len(result[key]) > 0:
                out_result[key] = result[key]

        return out_result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generates diff between two JSON files.")
    parser.add_argument("filenames", action="append", nargs=2,
                  metavar="FILENAME", help="names of the old and new JSON files")
    parser.add_argument("-x", "--exclude",
                  action="append", dest="exclude", default=[],
                  help="attributes which should be ignored when comparing")
    parser.add_argument("-H", "--HTML",
                  action="store_true", dest="HTMLoutput", default=False,
                  help="program should output to HTML report")
    parser.add_argument('--version', action='version', version='%(prog)s 0.1.1')
    options = parser.parse_args()

    diff = Comparator(file(options.filenames[0][0]), file(options.filenames[0][1]), options.exclude)
    if options.HTMLoutput:
        diff_res = diff.compare_dicts()
        logging.debug("diff_res:\n%s", json.dumps(diff_res, indent=True))
        print HTMLFormatter(diff_res)
    else:
        print json.dumps(diff.compare_dicts(), indent=4, ensure_ascii=False).encode("utf-8")
