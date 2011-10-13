#!/usr/bin/rhino
/*
This is for now just reimplementation of tlrobinson's json-diff (http://tlrobinson.net/projects/javascript-fun/jsondiff/).

However, later I would like to incorporate algorightm from
https://github.com/cmsd2/xdiff (which is an implementation in Ruby of
http://pages.cs.wisc.edu/~yuanwang/xdiff.html)
 */

var jsonBoxA, jsonBoxB;

//var HashStore = {
//  load : function(callback) {
//    if (window.location.hash) {
//      try {
//        var hashObject = JSON.parse(decodeURIComponent(window.location.hash.slice(1)));
//        callback && callback(hashObject.d);
//        return;
//      } catch (e) {
//        console.log()
//      }
//    }
//    callback && callback(null);
//  },
//  sync : function(object) {
//    var hashObject = { d : object };
//    window.location.hash = "#" + encodeURIComponent(JSON.stringify(hashObject));
//  }
//};

//function init() {
//  document.addEventListener("click", clickHandler, false);

//  jsonBoxA = document.getElementById("jsonA");
//  jsonBoxB = document.getElementById("jsonB");

//  HashStore.load(function(data) {
//    if (data) {
//      jsonBoxA.value = data.a;
//      jsonBoxB.value = data.b;
//    }
//  });

//  startCompare();
//}

//function startCompare() {
//  var aValue = jsonBoxA.value;
//  var bValue = jsonBoxB.value;

//  var objA, objB;
//  try {
//    objA = JSON.parse(aValue);
//    jsonBoxA.style.backgroundColor = "";
//  } catch(e) {
//    jsonBoxA.style.backgroundColor = "rgba(255,0,0,0.5)";
//  }
//  try {
//    objB = JSON.parse(bValue);
//    jsonBoxB.style.backgroundColor = "";
//  } catch(e) {
//    jsonBoxB.style.backgroundColor = "rgba(255,0,0,0.5)";
//  }

//  HashStore.sync({
//    a : aValue,
//    b : bValue
//  });

//  results = document.getElementById("results");
//  removeAllChildren(results);

//  compareTree(objA, objB, "root", results);
//}

function compareTree(a, b, name, results) {
  var typeA = typeofReal(a);
  var typeB = typeofReal(b);

  var typeSpanA = document.createElement("span");
  typeSpanA.appendChild(document.createTextNode("("+typeA+")"))
  typeSpanA.setAttribute("class", "typeName");

  var typeSpanB = document.createElement("span");
  typeSpanB.appendChild(document.createTextNode("("+typeB+")"))
  typeSpanB.setAttribute("class", "typeName");

  var aString = (typeA === "object" || typeA === "array") ? "" : String(a) + " ";
  var bString = (typeB === "object" || typeB === "array") ? "" : String(b) + " ";

  var leafNode = document.createElement("span");
  leafNode.appendChild(document.createTextNode(name));
  if (a === undefined) {
    leafNode.setAttribute("class", "added");
    leafNode.appendChild(document.createTextNode(": " + bString));
    leafNode.appendChild(typeSpanB);
  }
  else if (b === undefined) {
    leafNode.setAttribute("class", "removed");
    leafNode.appendChild(document.createTextNode(": " + aString));
    leafNode.appendChild(typeSpanA);
  }
  else if (typeA !== typeB || (typeA !== "object" && typeA !== "array" && a !== b)) {
    leafNode.setAttribute("class", "changed");
    leafNode.appendChild(document.createTextNode(": " + aString));
    leafNode.appendChild(typeSpanA);
    leafNode.appendChild(document.createTextNode(" => "+ bString));
    leafNode.appendChild(typeSpanB);
  }
  else {
    leafNode.appendChild(document.createTextNode(": " + aString));
    leafNode.appendChild(typeSpanA);
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

    var listNode = document.createElement("ul");
    listNode.appendChild(leafNode);

    for (var i = 0; i < keys.length; i++) {
      if (keys[i] === keys[i-1]) {
        continue;
      }
      var li = document.createElement("li");
      listNode.appendChild(li);

      compareTree(a && a[keys[i]], b && b[keys[i]], keys[i], li);
    }
    results.appendChild(listNode);
  }
  else {
    results.appendChild(leafNode);
  }
}

function removeAllChildren(node) {
  var child;
  while (child = node.lastChild) {
    node.removeChild(child);
  }
}

function typeofReal(value) {
  return Array.isArray(value) ? "array" : typeof value;
}

function clickHandler(e) {
  var e = e || window.event;
  if (e.target.nodeName.toUpperCase() === "UL") {
    if (e.target.getAttribute("closed") === "yes")
      e.target.setAttribute("closed", "no");
    else
      e.target.setAttribute("closed", "yes");
  }
}

/* vim: set ts=2 et sw=2 tw=80: */
