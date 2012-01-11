# coding: utf-8

NO_JSON_OLD = u"""
THIS IS NOT A JSON STRING
"""

NO_JSON_NEW = u"""
AND THIS NEITHER
"""

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

SIMPLE_DIFF = u"""
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

SIMPLE_DIFF_HTML = u"""
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

SIMPLE_ARRAY_OLD = u"""
{
   "a": [ 1 ]
}
"""

SIMPLE_ARRAY_NEW = u"""
{
   "a": [ 1, 2 ]
}
"""

SIMPLE_ARRAY_DIFF = u"""
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

NESTED_OLD = u"""
{
    "a": 1,
    "b": 2,
    "ignore": {
        "else": true
    },
    "child": {
        "nome": "Janošek"
    }
}
"""

NESTED_NEW = u"""
{
    "a": 2,
    "c": 3,
    "child": {
        "nome": "Maruška"
    }
}
"""

NESTED_DIFF = u"""
{
    "_append": {
        "c": 3
    },
    "_remove": {
        "b": 2,
        "ignore": {
            "else": true
        }
    },
    "_update": {
        "a": 2,
        "child": {
            "_update": {
                "nome": "Maruška"
            }
        }
    }
}
"""

NESTED_DIFF_EXCL = u"""
{
    "_append": {
        "c": 3
    },
    "_remove": {
        "b": 2,
        "ignore": {
            "else": true
        }
    },
    "_update": {
        "a": 2
    }
}
"""

NESTED_DIFF_INCL = u"""
{
    "_update": {
        "child": {
            "_update": {
                "nome": "Maruška"
            }
        }
    }
}
"""

NESTED_DIFF_IGNORING = u"""
{
    "_remove": {
        "b": 2,
        "ignore": {
            "else": true
        }
    },
    "_update": {
        "a": 2,
        "child": {
            "_update": {
                "nome": "Maruška"
            }
        }
    }
}
"""

ARRAY_OLD = u"""
{
    "a": 1,
    "b": 2,
    "children": [
        "Pepíček", "Anička", "Maruška"
    ]
}
"""

ARRAY_NEW = u"""
{
    "a": 1,
    "children": [
        "Pepíček", "Tonička", "Maruška"
    ],
    "c": 3
}
"""

ARRAY_DIFF = u"""
 {
    "_append": {
        "c": 3
    },
    "_remove": {
        "b": 2
    },
    "_update": {
        "children": {
            "_update": {
                "1": "Tonička"
            }
        }
    }
}
"""
