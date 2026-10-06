# CS351 - Lab 1: Python Warmup Guide

This document provides a complete guide and solution walkthrough for **Lab 1 (Python Warmup)**.

---

## Overview

- **Topics Covered**: String manipulation, list operations, dictionaries, sets, comprehensions, OOP class methods, and functional programming (`map`, `reduce`).
- **Files**: `Problem1.py` through `Problem14.py`

---

## Problem Summaries & Solutions

### Problem 1: String Breakdown
Convert a string into a list of characters.
- **Input**: `"abc"` -> **Output**: `['a', 'b', 'c']`
- **Execution**: `python Problem1.py`

### Problem 2: Reverse Character List
Join a list of characters back into a string.
- **Input**: `['a', 'b', 'c']` -> **Output**: `"abc"`
- **Execution**: `python Problem2.py`

### Problem 3: Random Number List
Generate a list of $n$ random numbers using the `random` module.
- **Input**: `5` -> **Output**: List of 5 random integers/floats.
- **Execution**: `python Problem3.py`

### Problem 4: Descending Sort
Sort a list of numbers in descending order.
- **Input**: `[1, 2, 3, 4, 5]` -> **Output**: `[5, 4, 3, 2, 1]`
- **Execution**: `python Problem4.py`

### Problem 5: Frequency Counter (`dict`)
Calculate frequency of elements in a list using a dictionary.
- **Input**: `[1,1,3,2,3,2,3,2,2]` -> **Output**: `{1: 2, 3: 3, 2: 4}`
- **Execution**: `python Problem5.py`

### Problem 6: Unique Elements (`set`)
Extract unique elements using a Python `set`.
- **Input**: `[1,1,3,2,3,2,3,2,2]` -> **Output**: `{1, 2, 3}`
- **Execution**: `python Problem6.py`

### Problem 7: First Repeating Element
Find the first repeating element in a list using a set.
- **Input**: `[1, 2, 3, 4, 5, 1, 2]` -> **Output**: `1`
- **Execution**: `python Problem7.py`

### Problem 8: Squares and Cubes Mapping
Generate a dictionary mapping numbers $0 \dots n$ to `[square, cube]`.
- **Input**: `3` -> **Output**: `{0: [0, 0], 1: [1, 1], 2: [4, 8], 3: [9, 27]}`
- **Execution**: `python Problem8.py`

### Problem 9: Element-wise Tuples (`zip`)
Combine two lists of equal size into list of tuples using `zip()`.
- **Input**: `[1,2,3,4]`, `['a','b','c','d']` -> **Output**: `[(1,'a'), (2,'b'), (3,'c'), (4,'d')]`
- **Execution**: `python Problem9.py`

### Problem 10: List Comprehension Squares
Generate list of squares $0 \dots n$ using list comprehension.
- **Input**: `5` -> **Output**: `[0, 1, 4, 9, 16, 25]`
- **Execution**: `python Problem10.py`

### Problem 11: Dictionary Comprehension
Generate mapping $0 \dots n$ to their squares using dictionary comprehension.
- **Input**: `5` -> **Output**: `{0: 0, 1: 1, 2: 4, 3: 9, 4: 16, 5: 25}`
- **Execution**: `python Problem11.py`

### Problem 12: Custom Class with `apply` Method
Class initializing a list and implementing `apply(func)` with error handling (`try/except`).
- **Execution**: `python Problem12.py`

### Problem 13: Functional Uppercase (`map`)
Uppercase list of strings using `map()`.
- **Input**: `['aa', 'bb', 'cd', 'e']` -> **Output**: `['AA', 'BB', 'CD', 'E']`
- **Execution**: `python Problem13.py`

### Problem 14: Functional Product (`functools.reduce`)
Compute product of all numbers in a list using `functools.reduce()`.
- **Input**: `[1, 2, 3, 4, 5]` -> **Output**: `120`
- **Execution**: `python Problem14.py`

---

## How to Run
Run any problem using Python 3:
```powershell
python Problem1.py
```
