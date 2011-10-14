#!/usr/bin/rhino -debug
var jsonBoxA, jsonBoxB;

//  compareTree(objA, objB, "root", results);

function JSONDiff(fn1, fn2) {
  this.obj1 = JSON.parse(readFile(fn1));
  this.obj2 = JSON.parse(readFile(fn2));
}

/**
 * Compare two objects recursively
 *
 *
 * For example, comparing object A
 *
 * { "a": 1,
 *   "b": 2,
 *   "son" : {
 *      "name": "Janošek"
 *    }
 * }
 *
 * and
 *
 * { "a": 2,
 *   "c": 3
 *   "daughter" : {
 *      "name": "Maruška"
 *    }
 * }
 *
 * we get
 *
 * {
 *   "insert": [
 *     { "c": 3 },
 *     {
 *       "daughter" : {
 *         "name": "Maruška"
 *       }
 *     }
 *    ],
 *   "delete": [
 *     { "b": 2 },
 *     {
 *       "son" : {
 *         "name": "Janošek"
 *       }
 *     }
 *    ],
 *   "update": { "a": 2 }
 *    ]
 * }
 */
JSONDiff.prototype.compareTree = function compareTree(a, b, name) {
  function typeofReal(value) {
    return Array.isArray(value) ? "array" : typeof value;
  }
  
  function isScalar(value) {
    var typeStr = typeofReal(value);
    return !((typeStr == "array") || (typeStr == "object"));
  }

  var equal = false;
  var elements = {};
  
  for (var key in a) {
    if a.hasOwnProperty(key) {
      elements[key] = null;
    }
  }
  for (var key in b) {
    if b.hasOwnProperty(key) {
      elements[key] = null;
    }
  }

//  print("compareTree: name = " + name);
  var typeA = typeofReal(a);
  var typeB = typeofReal(b);

  if (typeA !== typeB) {
    // There is not much to be done when the objects are not of
    // the same type
    return {
      'deleted': a,
      'inserted': b
    }
  }

  // Now we have both objects of the same type, so
  // we can evaluate just type of one
  // If it is array ...
  if (typeA === "array") {
    var results = {
      'updated': {}
    };
    var maxLen = a.length > b.length ? a.length : b.length;
    for (var i = 0; i < maxLen; i++) {
      if (isScalar(a[i]) && isScalar(b[i])) {
        if (a[i] !== b[i]) {
          results['updated'][i] = b[i];
        }
      }
    }
  }
  
  if (typeA === "object") {
  }

/*
two trees are equal when:
- they have same keys,
- properties of the same keys have same values
====
if keys are not same, then whole subobject ==> ADDED/DELETED
if property values are not same && value is scalar, ==> UPDATED
if trees are not same, go one level down and compare two siblings
 */

  if (a === undefined) {
    this.results['inserted'].push(b);
  }
  else if (b === undefined) {
    this.results['deleted'].push(a);
  }
  else if (typeA !== typeB || (typeA !== "object" && typeA !== "array" && a !== b)) {
    this.results['updated'].push(b);
  }

  if (typeA === "object" || typeA === "array" || typeB === "object" || typeB === "array") {
    var keys = [];
    for (var i in a) {
      if (a.hasOwnProperty(i)) {
        keys.push(i);
      }
    }
    for (var i in b) {
      if (b.hasOwnProperty(i)) {
        keys.push(i);
      }
    }
    keys.sort();

    for (var i = 0; i < keys.length; i++) {
      if (keys[i] === keys[i-1]) {
        continue;
      }
      this.compareTree(a && a[keys[i]], b && b[keys[i]], keys[i]);
    }
  }
};

JSONDiff.prototype.diff = function diff() {
  this.compareTree(this.obj1, this.obj2, "root");
  return this.results;
};

if (arguments.length == 2) {
  var diffObj = new JSONDiff(arguments[0], arguments[1]);
//  print(diffObj);
  var diff = diffObj.diff();
  print (JSON.stringify(diff));
}


/* vim: set ts=2 et sw=2 tw=80: */
