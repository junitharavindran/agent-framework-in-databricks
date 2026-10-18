"""
The wiki: ~10 short pages for the Python tutor agent.

Deliberately MISSING: exceptions (try/except) and classes. The eval set asks about them, so we can watch the agent answer from the model's memory instead of the wiki.
"""

WIKI_PAGES = {
    "variables": (
        "Variables store values. Create one by assigning: `age = 30`. "
        "Names are case-sensitive and cannot start with a digit. "
        "Python infers the type, so you never declare it."
    ),
    "data_types": (
        "Common built-in types: int (`5`), float (`5.0`), str (`'hi'`), bool (`True`). "
        "Check a type with `type(x)`. Convert with `int('5')`, `str(5)`, `float('1.5')`."
    ),
    "strings": (
        "Strings hold text in single or double quotes. Use f-strings to embed values: "
        "`name = 'Ada'; print(f'Hello {name}')`. Useful methods: `.upper()`, `.lower()`, "
        "`.strip()`, `.split()`. Slice with `s[0:3]`."
    ),
    "lists": (
        "Lists are ordered, changeable collections: `nums = [1, 2, 3]`. "
        "Add with `nums.append(4)`, remove with `nums.remove(2)`. "
        "Index from 0: `nums[0]`. Get the length with `len(nums)`."
    ),
    "dictionaries": (
        "Dictionaries map keys to values: `ages = {'ada': 36, 'alan': 41}`. "
        "Read with `ages['ada']` or `ages.get('bob', 0)` (safe default). "
        "Add or change with `ages['bob'] = 25`. Loop with `for k, v in ages.items():`."
    ),
    "conditionals": (
        "Use `if`, `elif` and `else` to choose a path: "
        "`if x > 0: print('positive') elif x == 0: print('zero') else: print('negative')`. "
        "Indentation (4 spaces) defines the block. Combine tests with `and`, `or`, `not`."
    ),
    "loops": (
        "`for` loops iterate over a sequence: `for n in [1, 2, 3]: print(n)`. "
        "`range(5)` gives 0 to 4. `while` repeats while a condition is true. "
        "Use `break` to stop early and `continue` to skip to the next item."
    ),
    "functions": (
        "Define a function with `def`: `def add(a, b): return a + b`. "
        "Call it with `add(2, 3)`. Parameters can have defaults: `def greet(name='friend')`. "
        "A function without `return` gives back `None`."
    ),
    "modules": (
        "A module is a Python file you can reuse. Import with `import math` and use "
        "`math.sqrt(16)`, or `from math import sqrt`. The standard library ships many "
        "modules, e.g. `random`, `datetime`, `json`."
    ),
    "files": (
        "Open files with a context manager so they close automatically: "
        "`with open('notes.txt') as f: text = f.read()`. "
        "Use mode `'w'` to write and `'a'` to append."
    ),
}
