#!/usr/bin/env python3
# Name: Sayan Shit
# Roll No: 2401179

import sys

def combine_word_counts():

    current_word = None
    current_count = 0

    for raw_line in sys.stdin:
        cleaned_line = raw_line.strip()
        if not cleaned_line:
            continue

        try:
            word, count_str = cleaned_line.rsplit(',', 1)
            count = int(count_str)
        except ValueError:
            continue

        # If incoming word matches the active group, accumulate locally
        if current_word == word:
            current_count += count
        else:
            # Emit subtotal for the previous word
            if current_word is not None:
                print("{0},{1}".format(current_word, current_count))
            current_word = word
            current_count = count

    # Emit the last accumulated word
    if current_word is not None:
        print("{0},{1}".format(current_word, current_count))

if __name__ == "__main__":
    combine_word_counts()
