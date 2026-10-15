#!/usr/bin/env python3
# Name: Sayan Shit
# Roll No: 2401179

import sys

def reduce_distinct_words():

    current_word = None

    # Process line-by-line from sorted standard input stream
    for raw_line in sys.stdin:
        cleaned_line = raw_line.strip()
        if not cleaned_line:
            continue

        # Extract the word (key) by splitting on the comma delimiter
        try:
            word, _ = cleaned_line.rsplit(',', 1)
        except ValueError:
            # Fallback if line does not contain comma delimiter
            word = cleaned_line

        # Emit the word only when transitioning to a new unique word
        if current_word != word:
            if current_word is not None:
                print(current_word)
            current_word = word

    # Emit the final unique word after stream terminates
    if current_word is not None:
        print(current_word)

if __name__ == "__main__":
    reduce_distinct_words()
