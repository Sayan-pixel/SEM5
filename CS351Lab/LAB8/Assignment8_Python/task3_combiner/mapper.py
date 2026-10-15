#!/usr/bin/env python3
# Name: Sayan Shit
# Roll No: 2401179

import sys

def map_word_tokens():

    for raw_line in sys.stdin:
        cleaned_line = raw_line.strip()
        if not cleaned_line:
            continue

        words = cleaned_line.split()
        for word in words:
            print("{0},1".format(word))

if __name__ == "__main__":
    map_word_tokens()
