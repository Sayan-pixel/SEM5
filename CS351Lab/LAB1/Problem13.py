def uppercase_words(words):
    return list(map(str.upper, words))

words = input("Enter another list of character: ").split()
print(f"Output: {uppercase_words(words)}")
