def list_into_string(li):
    res = "".join(li)
    return res

li = input("Enter elements separated by space: ").split()
print("List:", li)
print("String", list_into_string(li))