def generate_square_mapping(n):
    return {i: i**2 for i in range(n + 1)}

n = (int (input("Enter a number: ")))
print(f"Output: {generate_square_mapping(n)}")