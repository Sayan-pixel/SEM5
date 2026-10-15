#!/usr/bin/env python3
# Name: Sayan Shit
# Roll No: 2401179

import sys
import string

def clean_and_map_words():

    # Create a set of punctuation characters for O(1) lookup
    punctuation_characters = set(string.punctuation)

    # Read line-by-line from standard input
    for raw_line in sys.stdin:
        # Step 1: Remove all punctuation characters
        cleaned_chars = [ch for ch in raw_line if ch not in punctuation_characters]
        line_without_punctuation = "".join(cleaned_chars)

        # Step 2: Convert entire line to lowercase
        normalized_lowercase_line = line_without_punctuation.lower()

        # Step 3: Tokenize into words by whitespace
        word_tokens = normalized_lowercase_line.split()

        # Step 4: Emit each cleaned word with dummy count 1
        for word in word_tokens:
            print("{0},1".format(word))

if __name__ == "__main__":
    clean_and_map_words()
