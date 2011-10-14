#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Script for comparing two objects
"""
import json
from optparse import OptionParser
import logging

logging.basicConfig(format='%(levelname)s:%(funcName)s:%(message)s', level=logging.INFO)

class Comparator(object):
    """
    Main workhorse, the object itself 
    """
    def __init__(self, fn1=None, fn2=None, excluded_attrs=()):
        if fn1:
            self.obj1 = json.load(fn1)
        if fn2:
            self.obj2 = json.load(fn2)
        self.excluded_attributes = excluded_attrs
        if (fn1 and fn2):
            logging.debug("self.obj1 = %s\nself.obj2 = %s\nself.excluded_attrs = %s", \
                          (self.obj1, self.obj2, self.excluded_attributes))

    @staticmethod
    def _get_keys(obj):
        """
        Getter for the current object's keys.
        """
        out = set()
        for key in obj.keys():
            out.add(key)
        return out
    
    @staticmethod
    def _is_scalar(value):
        """
        Primitive version, relying on the fact that JSON cannot
        contain any more complicated data structures.
        """
        return not isinstance(value, (list, tuple, dict))

    def _compare_arrays(self, old_arr, new_arr):
        inters = min(old_arr, new_arr)

        result = {
            u"append": {},
            u"remove": {},
            u"update": {}
        }        
        for idx in range(len(inters)):
            # changed objects, new value is new_arr
            if (type(old_arr[idx]) != type(new_arr[idx])):
                result['update'][idx] = new_arr[idx]
            # another simple variant ... scalars
            elif (self._is_scalar(old_arr)):
                if old_arr[idx] != new_arr[idx]:
                    result['update'][idx] = new_arr[idx]
            # recursive arrays
            elif (isinstance(old_arr[idx], list)):
                res_arr = self._compare_arrays(old_arr[idx], \
                    new_arr[idx])
                if (len(res_arr) > 0):
                    result['update'][idx] = res_arr
            # and now nested dicts
            elif isinstance(old_arr[idx], dict):
                res_dict = self.compare_dicts(old_arr[idx], new_arr[idx])
                if (len(res_dict) > 0):
                    result['update'][idx] = res_dict
    
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
            old_keys = self._get_keys(old_obj)
        if new_obj and len(new_obj) > 0:
            new_keys = self._get_keys(new_obj)

        keys = old_keys | new_keys

        result = {
            u"append": {},
            u"remove": {},
            u"update": {}
        }        
        for name in keys:
            # Explicitly excluded arguments
            if (name in self.excluded_attributes):
                continue
            # old_obj is missing
            if name not in old_obj:
                result['append'][name] = new_obj[name]
            # new_obj is missing
            elif name not in new_obj:
                result['remove'][name] = old_obj[name]
            # changed objects, new value is new_obj
            elif (type(old_obj[name]) != type(new_obj[name])):
                result['update'][name] = new_obj[name]
            # last simple variant ... scalars
            elif (self._is_scalar(old_obj[name])):
                if old_obj[name] != new_obj[name]:
                    result['update'][name] = new_obj[name]
            # now arrays
            elif (isinstance(old_obj[name], list)):
                res_arr = self._compare_arrays(old_obj[name], \
                    new_obj[name])
                if (len(res_arr) > 0):
                    result['update'][name] = res_arr
            # and now nested dicts
            elif isinstance(old_obj[name], dict):
                res_dict = self.compare_dicts(old_obj[name], new_obj[name])
                if (len(res_dict) > 0):
                    result['update'][name] = res_dict
    
        # Clear out unused keys in result
        out_result = {}
        for key in result:
            if len(result[key]) > 0:
                out_result[key] = result[key]
        
        return out_result


if __name__ == "__main__":
    usage = "usage: %prog [options] old.json new.json"
    parser = OptionParser(usage=usage)
    parser.add_option("-x", "--exclude",
                  action="append", dest="exclude", metavar="ATTR", default=[],
                  help="attributes which should be ignored when comparing")
    (options, args) = parser.parse_args()
    logging.debug("options = %s", str(options))
    logging.debug("args = %s", str(args))
    if len(args) != 2:
        parser.error("Script requires two positional arguments, names for old and new JSON file.")
    
    diff = Comparator(file(args[0]), file(args[1]), options.exclude)
    print json.dumps(diff.compare_dicts(), indent=4, ensure_ascii=False)