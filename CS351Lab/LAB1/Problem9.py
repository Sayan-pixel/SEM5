def zip_lists(list1, list2):
    return list(zip(list1, list2))

list1 = list(map(int, input("Enter a list of numbers: ").split()))
list2 = input("Enter another list of character: ").split()

print(f"Input: {list1}, {list2}")
print(f"Output: {zip_lists(list1, list2)}")