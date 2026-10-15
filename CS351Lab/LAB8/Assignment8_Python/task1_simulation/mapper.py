#!/usr/bin/env python3
# Name: Sayan Shit
# Roll No: 2401179

import sys

def map_words():
    
    # Iterate line by line through standard input (streamed by Hadoop or pipe)
    for raw_line in sys.stdin:
        # Strip leading and trailing whitespace characters (including newlines)
        cleaned_line = raw_line.strip()
        
        # Skip empty lines
        if not cleaned_line:
            continue
            
        # Split the cleaned line into individual words based on whitespace
        word_tokens = cleaned_line.split()
        
        # Emit each word with a count of 1, separated by comma as specified in the assignment
        for word in word_tokens:
            print("{0},1".format(word))

if __name__ == "__main__":
    map_words()
