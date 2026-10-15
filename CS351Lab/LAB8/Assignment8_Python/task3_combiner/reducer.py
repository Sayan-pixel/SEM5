#!/usr/bin/env python3
# Name: Sayan Shit
# Roll No: 2401179

import sys

def reduce_final_word_counts():

    current_word = None
    grand_total = 0

    for raw_line in sys.stdin:
        cleaned_line = raw_line.strip()
        if not cleaned_line:
            continue

        try:
            word, subtotal_str = cleaned_line.rsplit(',', 1)
            subtotal = int(subtotal_str)
        except ValueError:
            continue

        # Accumulate subtotals for the same key
        if current_word == word:
            grand_total += subtotal
        else:
            if current_word is not None:
                print("{0},{1}".format(current_word, grand_total))
            current_word = word
            grand_total = subtotal

    # Emit the last accumulated key
    if current_word is not None:
        print("{0},{1}".format(current_word, grand_total))

if __name__ == "__main__":
    reduce_final_word_counts()
