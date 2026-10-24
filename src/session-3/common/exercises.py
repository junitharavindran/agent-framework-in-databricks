"""
Practice exercises for the Python tutor: one per wiki page, keyed by the same page ids.

This is data the wiki does not hold, which is why a tool is needed to get it (06_tools.py, T1).
"""

EXERCISES = {
    "variables": {
        "exercise": "Store your name and age in two variables, then print them on one line.",
        "hint": "Assign with `=`, then pass both variables to `print()`.",
    },
    "data_types": {
        "exercise": "Convert the string '42' to an int, add 8, and print the result and its type.",
        "hint": "Use `int()` and `type()`.",
    },
    "strings": {
        "exercise": "Given `name = 'ada'`, print `Hello, ADA!` using an f-string and `.upper()`.",
        "hint": "An f-string can call a method inside the braces.",
    },
    "lists": {
        "exercise": "Start with `nums = [3, 1, 2]`. Add 4, remove 1, then print the list and its length.",
        "hint": "Use `append`, `remove` and `len`.",
    },
    "dictionaries": {
        "exercise": (
            "Make a dictionary of three people and their ages. Print each as `name: age`, "
            "then look up a person who is not in it without raising an error."
        ),
        "hint": "Loop with `.items()`; look up with `.get()` and a default.",
    },
    "conditionals": {
        "exercise": "Print `positive`, `zero` or `negative` for a number `x`.",
        "hint": "Use `if`, `elif` and `else`.",
    },
    "loops": {
        "exercise": "Print the numbers 0 to 4. Then loop over `[1, 2, 3, 4]` and stop as soon as you reach 3.",
        "hint": "Use `range(5)` for the first part and `break` for the second.",
    },
    "functions": {
        "exercise": "Write `greet(name='friend')` that returns a greeting. Call it with and without an argument.",
        "hint": "A function without `return` gives back `None`, so remember to `return`.",
    },
    "modules": {
        "exercise": "Use the `random` module to print a random whole number from 1 to 6.",
        "hint": "Start with `import random`, then look for `randint`.",
    },
    "files": {
        "exercise": "Write two lines to `notes.txt`, then read the file back and print it.",
        "hint": "Use `with open(...)` in mode `'w'`, then open the file again to read it.",
    },
}


def exercise_text(topic_id: str) -> str:
    """The exercise for a topic as one string. The UC function returns the same text."""
    e = EXERCISES.get(topic_id)
    return f"Exercise: {e['exercise']} Hint: {e['hint']}" if e else "No exercise for that topic."