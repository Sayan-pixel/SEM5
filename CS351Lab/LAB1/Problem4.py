def list_num_descending_order(li):
    li.sort(reverse=True)
    # lst.sort(key=None, reverse=False) -> Syntax
    return li

li = list(map(int, input("Enter a list of numbers: ").split()))
print(list_num_descending_order(li))