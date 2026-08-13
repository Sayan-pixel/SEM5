import functools

def product_of_list(li):
    return functools.reduce(lambda x, y: x * y, li)

li = list(map(int, input("Enter a list of numbers: ").split()))
print(f"Output: {product_of_list(li)}")