def first_repeating_element(li):
    visited = set()
    for num in li:
        if num in visited:
            return num
        visited.add(num)
    return None

li = list(map(int, input("Enter a list of numbers: ").split()))
print("Input List:", li)
print("Output:", first_repeating_element(li))
