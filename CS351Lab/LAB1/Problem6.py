def get_unique_elements(li):
    return set(li)

li = list(map(int, input("Enter a list of numbers: ").split()))
print("Input List:", li)
print("Output:", get_unique_elements(li))
