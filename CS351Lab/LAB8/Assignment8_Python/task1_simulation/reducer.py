#!/usr/bin/env python3
# Name: Sayan Shit
# Roll No: 2401179

import sys

def reduce_word_counts():

    current_word = None
    current_count = 0

    # Iterate line by line through standard input
    for raw_line in sys.stdin:
        cleaned_line = raw_line.strip()
        
        # Skip empty lines
        if not cleaned_line:
            continue

        # Parse key and value separated by comma
        try:
            word, count_str = cleaned_line.rsplit(',', 1)
            count = int(count_str)
        except ValueError:
            # Skip records that do not strictly match 'word,count' format
            continue

        # If incoming word matches the active group, accumulate count
        if current_word == word:
            current_count += count
        else:
            # If transitioning to a new word, emit the completed group
            if current_word is not None:
                print("{0},{1}".format(current_word, current_count))
            
            # Start tracking the new word
            current_word = word
            current_count = count

    # Emit the last accumulated word group after the stream finishes
    if current_word is not None:
        print("{0},{1}".format(current_word, current_count))

if __name__ == "__main__":
    reduce_word_counts()
